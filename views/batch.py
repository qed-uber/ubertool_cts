from django.template.loader import render_to_string
from django.http import HttpResponse
import importlib
import linksLeft
import links_left
import os
import logging
from cts_app.models.pchemprop import pchemprop_tables
from cts_app.cts_api import cts_rest
import datetime

def batchInputPage(request, model='none', header='none'):
    viewmodule = importlib.import_module('.views', 'cts_app.models.'+model)
    inputmodule = importlib.import_module('.'+model+'_batch', 'cts_app.models.'+model)
    header = viewmodule.header
    

    #drupal template for header with bluestripe
    html = render_to_string('01epa_drupal_header.html', {
        'SITE_SKIN': os.environ['SITE_SKIN'],
        'TITLE': "CTS"
    })

    html += render_to_string('02epa_drupal_header_bluestripe_onesidebar.html', {})
    html += render_to_string('03epa_drupal_section_title_cts.html', {})

    html += render_to_string('06ubertext_start_index_drupal.html', {
        # 'TITLE': 'Calculate Chemical Speciation',
        # 'TEXT_PARAGRAPH': xx
    })


    html = html + render_to_string('04cts_uberbatchinput.html', {
            'model': model,
            'model_attributes': header+' Batch Run'})
    html += render_to_string('04cts_uberinput_jquery.html', { 'model': model}) # loads scripts_pchemprop.js
    inputPageFunc = getattr(inputmodule, model+'BatchInputPage')  # function name = 'model'InputPage  (e.g. 'sipInputPage')
    html = html + inputPageFunc(request, model, header)
    html = html + render_to_string('04cts_uberbatchinput_jquery.html', {'model':model, 'header':header})


    html += render_to_string('07ubertext_end_drupal.html', {})
    # html += links_left.ordered_list(model='cts/' + model)  # fills out 05ubertext_links_left_drupal.html
    html += links_left.ordered_list(model='cts/' + model, page='batch')

    #scripts and footer
    html += render_to_string('09epa_drupal_ubertool_css.html', {})
    html += render_to_string('09epa_drupal_cts_css.html')
    html += render_to_string('09epa_drupal_cts_scripts.html')
    #html += render_to_string('09epa_drupal_ubertool_scripts.html', {})
    html += render_to_string('10epa_drupal_footer.html', {})


    # html = render_to_string('01cts_uberheader.html', {'title': header+' Batch'})
    # html = html + render_to_string('02cts_uberintroblock_wmodellinks.html', {'model':model,'page':'batchinput'})
    # html = html + linksLeft.linksLeft()
    # html = html + render_to_string('04cts_uberbatchinput.html', {
    #         'model': model,
    #         'model_attributes': header+' Batch Run'})

    # html += render_to_string('04cts_uberinput_jquery.html', { 'model': model}) # loads scripts_pchemprop.js


    # inputPageFunc = getattr(inputmodule, model+'BatchInputPage')  # function name = 'model'InputPage  (e.g. 'sipInputPage')
    # html = html + inputPageFunc(request, model, header)


    # html = html + render_to_string('04cts_uberbatchinput_jquery.html', {'model':model, 'header':header})
    
    # # html = html + render_to_string('05cts_ubertext_links_right.html', {})
    # html = html + render_to_string('06cts_uberfooter.html', {'links': ''})

    response = HttpResponse()
    response.write(html)
    return response

def batchOutputPage(request, model='none', header='none'):
    viewmodule = importlib.import_module('.views', 'cts_app.models.'+model)
    batchoutputmodule = importlib.import_module('.'+model+'_batch', 'cts_app.models.'+model)
    header = viewmodule.header
    


    #drupal template for header with bluestripe
    html = render_to_string('01epa_drupal_header.html', {
        'SITE_SKIN': os.environ['SITE_SKIN'],
        'TITLE': "CTS"
    })

    html += render_to_string('02epa_drupal_header_bluestripe_onesidebar.html', {})
    html += render_to_string('03epa_drupal_section_title_cts.html', {})

    html += render_to_string('06ubertext_start_index_drupal.html', {
        # 'TITLE': 'Calculate Chemical Speciation',
        # 'TEXT_PARAGRAPH': xx
    })

    html += render_to_string('04cts_uberbatch_start.html', {
            'model': model,
            'model_attributes': header+' Batch Output'})

    # timestamp / version section
    st = datetime.datetime.strptime(cts_rest.gen_jid(), 
        '%Y%m%d%H%M%S%f').strftime('%A, %Y-%B-%d %H:%M:%S')
    html += """
    <div class="out_">
        <b>{} Batch Version 1.0</a> (Beta)<br>
    """.format(header)
    html += st
    html += " (EST)</b>"
    html += """
    </div><br><br>"""

    html = html + render_to_string('cts_export.html', {})

    batchOutputPageFunc = getattr(batchoutputmodule, model+'BatchOutputPage')  # function name = 'model'BatchOutputPage  (e.g. 'sipBatchOutputPage')
    html += batchOutputPageFunc(request)

    html = html + render_to_string('04cts_uberoutput_end.html', {})

    html += render_to_string('07ubertext_end_drupal.html', {})
    # html += links_left.ordered_list(model='cts/' + model)  # fills out 05ubertext_links_left_drupal.html
    html += links_left.ordered_list(model='cts/' + model, page='batchoutput')

    #scripts and footer
    html += render_to_string('09epa_drupal_ubertool_css.html', {})
    html += render_to_string('09epa_drupal_cts_css.html')
    html += render_to_string('09epa_drupal_cts_scripts.html')
    #html += render_to_string('09epa_drupal_ubertool_scripts.html', {})
    html += render_to_string('10epa_drupal_footer.html', {})


    response = HttpResponse()
    response.write(html)
    return response