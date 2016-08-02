import os
os.environ['DJANGO_SETTINGS_MODULE']='settings'
from django.template.loader import render_to_string
from models.pchemprop import pchemprop_parameters
import json


def pchempropBatchInputPage(request, model='', header='P-Chem Properties', formData=None):
    """
    Currently, I'm using these model specific batch input page functions
    for drawing the models' unique input selection. For pchemprop, the p-chem
    appears after the user has uploaded a chemical file for batch
    """

    # for pchemprop batch, use p-chem for selecting inputs for batch data:
    html = """
    <div id="pchem_batch_wrap" hidden>
        <h3>1. Select p-chem properties for batch chemicals</h3>
    """

    html += render_to_string('cts_pchem.html', {})

    html += """
        <div class="input_nav">
            <div class="input_right">
                <input type="button" value="Clear" id="clearbutton" class="input_button">
                <input class="submit input_button" type="submit" value="Submit">
            </div>
        </div>
    </div>
    """

    return html


def pchempropBatchOutputPage(request, model='', header='P-Chem Properties', formData=None):

    # get all the fields from the form in the request, then
    # instantiate model object to get checkedCalcsAndProps dict.
    # render said dict into cts_pchemprop_ajax_calls template

    from models.pchemprop import pchemprop_output
    from django.utils.safestring import mark_safe

    pchemprop_obj = pchemprop_output.pchempropOutputPage(request)
    batch_chemicals = request.POST.get('nodes')  # expecting list of nodes (change name??)

    if not batch_chemicals:
        batch_chemicals = []

    html = render_to_string('cts_downloads.html', 
        {'run_data': mark_safe(json.dumps(pchemprop_obj.run_data))})

    html += '<link rel="stylesheet" href="//code.jquery.com/ui/1.11.2/themes/smoothness/jquery-ui.css">'

    # for pchemprop batch, use p-chem for selecting inputs for batch data:
    html +=  render_to_string('cts_pchemprop_ajax_calls.html', 
        {'checkedCalcsAndProps': mark_safe(pchemprop_obj.checkedCalcsAndPropsDict),
        'kow_ph': pchemprop_obj.kow_ph,
        'nodes': mark_safe(batch_chemicals)})

    html += render_to_string('cts_gentrans_tree.html', {'gen_max': 0})


    # what about other places cts_pchemprop_ajax_calls is rendered WITHOUT "nodes"???


    # display content on the output page:
    # html += '<div id="batch_csv_wrap" hidden></div>'


    return html