from django.views.decorators.http import require_POST
import StringIO
from django.http import HttpResponse
from django.conf import settings
from django.template import Context
import datetime
import pytz
import json
import os
import pdfkit

import logging
from models.gentrans import data_walks
from models.gentrans.gentrans_tables import buildMetaboliteTableForPDF
from chemaxon_cts.jchem_rest import gen_jid
import csv
from django.core.cache import cache



def parsePOST(request):

    pdf_t = request.POST.get('pdf_t')
    pdf_nop = request.POST.get('pdf_nop')
    pdf_p = json.loads(request.POST.get('pdf_p'))
    if 'pdf_json' in request.POST and request.POST['pdf_json']:
        pdf_json = json.loads(request.POST.get('pdf_json'))
        # pdf_json = request.POST.get('pdf_json')
    else:
        pdf_json = None

    # Append strings and check if charts are present
    final_str = pdf_t

    if 'gentrans' in request.path:
        # TODO: class this, e.g., Metabolizer (jchem_rest)
        # headings = ['genKey', 'smiles', 'water_sol', 'ion_con', 'kow_no_ph', 'kow_wph', 'image']
        headings = ['genKey', 'smiles', 'melting_point', 'boiling_point', 'water_sol', 'vapor_press',
                    'mol_diss', 'ion_con', 'henrys_law_con', 'kow_no_ph', 'kow_wph', 'koc', 'image']
        metaboliteList = data_walks.buildTableValues(pdf_json, headings, 3)  # List of dicts, which are node data
        final_str += buildMetaboliteTableForPDF().render(Context(dict(headings=headings, metaboliteList=metaboliteList)))

    final_str += """<br>"""
    if (int(pdf_nop)>0):
        for i in range(int(pdf_nop)):
            final_str += """<img id="imgChart1" src="%s" />"""%(pdf_p[i])
            # final_str = final_str + """<br>"""

    # Styling
    input_css="""
            <style>

            body {font-family: 'Open Sans', sans-serif;}
            table, td, th {
                border: 1px solid #666666;
            }
            #gentrans_table td {
                /*word-wrap: normal;*/
                max-width: 100px;
                word-break: break-all;
            }
            table#inputsTable td {
                max-width: 600px;
                word-break: break-all;
            }
            table {border-collapse: collapse;}
            th {text-align:center; padding:2px; font-size:11px;}
            td {padding:2px; font-size:10px;}
            h2 {font-size:13px; color:#79973F;}
            h3 {font-size:12px; color:#79973F; margin-top: 8px;}
            h4 {font-size:12px; color:#79973F; padding-top:30px;}
            .pdfDiv {border: 1px solid #000000;}
            div.tooltiptext {display: table; border: 1px solid #333333; margin: 8px; padding: 4px}

            </style>
            """
    input_str = input_css + final_str

    return input_str


@require_POST
def pdfReceiver(request, model=''):
    """
    PDF Generation Receiver function.
    Sends POST data as string to pdfkit library for processing
    """
    input_str = ''
    input_str += parsePOST(request)
    packet = StringIO.StringIO(input_str) #write to memory
    config = pdfkit.configuration(wkhtmltopdf=os.environ['wkhtmltopdf'])
    # landscape only for metabolites output:
    if 'pdf_json' in request.POST and request.POST['pdf_json']:
        options = {'orientation': 'Landscape'}
    else:
        options = {'orientation': 'Portrait'}
    pdf = pdfkit.from_string(input_str, False, configuration=config, options=options)
    jid = gen_jid() # create timestamp
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + model + '_' + jid + '.pdf'
    # packet.truncate(0)  # clear from memory?
    packet.close()  # todo: figure out why this doesn't solve the 'caching problem'
    return response


@require_POST
def htmlReceiver(request, model=''):
    """
    Save output as HTML
    """
    input_str = ''
    input_str += parsePOST(request)
    packet = StringIO.StringIO(input_str)  # write to memory
    jid = gen_jid() # create timestamp
    response = HttpResponse(packet.getvalue(), content_type='application/html')
    response['Content-Disposition'] = 'attachment; filename=' + model + '_' + jid + '.html'
    # packet.truncate(0)  # clear from memory?
    packet.close()
    return response


class CSV(object):
    def __init__(self, model):
        self.models = ['chemspec', 'pchemprop', 'gentrans']
        self.calcs = ['chemaxon', 'epi', 'test', 'sparc']
        if model and (model in self.models):
            self.model = model # model name
        else:
            raise KeyError("Model - {} - not accepted..".format(model))
        self.title = '' # workflow title
        self.time = '' # time of run
        self.csv_rows = {
            'header_row': [],
            'row_1': [] # row_n keys for batch mode
        } # list of ordered csv rows
        self.parent_info = ['smiles', 'name', 'mass', 'formula'] # original user sructure
        self.header_row = [] # headers in order (per molecule)
        self.data_row = [] # data in order w/ headers
        self.run_json = '' # json str from [model]_model.py
        self.run_data = {} # run_json as an object

    def parseToCSV(self, run_data):
        jid = gen_jid() # create timestamp
        time_str = datetime.datetime.strptime(jid, '%Y%m%d%H%M%S%f').strftime('%A, %Y-%B-%d %H:%M:%S')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + self.model + '_' + jid + '.csv'

        writer = csv.writer(response) # bind writer to http response

        # build title section of csv..
        writer.writerow([run_data['title']])
        writer.writerow([run_data['time']])
        writer.writerow([""])

        # write parent info first and in order..
        for prop in self.parent_info:
            for key, val in run_data.items():
                if key == prop:
                    self.csv_rows['header_row'].append(key)
                    self.csv_rows['row_1'].append(val)

        if self.model == 'chemspec':
            for key, val in run_data.items():
                if key not in self.parent_info:
                    if key == 'isoelectricPoint':
                        self.csv_rows['header_row'].append(key)
                        self.csv_rows['row_1'].append(val)
                    elif key == 'pka' or key == 'pkb':
                        i = 0 # pka counter
                        for item in val:
                            self.csv_rows['header_row'].append(key + str(i))
                            self.csv_rows['row_1'].append(item)
                            i+=1
                    elif key == 'pka-parent' or key == 'majorMicrospecies':
                        self.csv_rows['header_row'].append(key + '-smiles')
                        self.csv_rows['row_1'].append(val['smiles'])
                    elif key == 'pka-micospecies':
                        for ms in val.items():
                            # each ms is a jchem_structure object
                            self.csv_rows['header_row'].append(key + '-smiles')
                            self.csv_rows['row_1'].append(val['smiles'])
                    elif key == 'stereoisomers' or key == 'tautomers':
                        i = 0
                        for item in val:
                            self.csv_rows['header_row'].append(item['key'] + str(i))
                            self.csv_rows['row_1'].append(item['smiles'])
                            i+=1

        elif self.model == 'pchemprop':
            # TODO: Probably want props grouped together so it's easier to compare..
            # ^ This could be a bit challenging uness run_data is changed to be 
            # indexed by prop instead of calc..
            for key, val in run_data.items():
                if key in self.calcs:
                    for prop, prop_val in val.items():
                        if prop == "ion_con":
                            # prop_val is dict w/ key:values of "pkan": "pkan val"..
                            for pka_key, pka_val in prop_val.items():
                                self.csv_rows['header_row'].append(key + '-' + pka_key)
                                self.csv_rows['row_1'].append(pka_val)
                        else:   
                            self.csv_rows['header_row'].append(key + '-' + prop)
                            self.csv_rows['row_1'].append(prop_val)

        writer.writerow(self.csv_rows['header_row'])
        writer.writerow(self.csv_rows['row_1'])

        return response


@require_POST
def csvReceiver(request, model=''):
    """
    Save output as CSV
    """
    if model == 'chemspec':
        try:
            run_json = cache.get('run_json') # todo: add error handling
            cache.delete('run_json')
            run_data = json.loads(run_json)
        except Exception as err:
            raise err

    elif model == 'pchemprop':
        try:
            run_json = cache.get('run_json') # get parent info from cache
            cache.delete('run_json')
            run_data = json.loads(run_json)

            json_data = request.POST.get('pdf_json') # checkCalcsAndProps dict
            run_data.update(json.loads(json_data))
        except Exception as err:
            raise err

    csv_obj = CSV(model)
    return csv_obj.parseToCSV(run_data)