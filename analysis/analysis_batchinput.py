import os
os.environ['DJANGO_SETTINGS_MODULE']='settings'
import webapp2 as webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import numpy as np
import cgi
import cgitb
cgitb.enable()

class analysisBatchInputPage(webapp.RequestHandler):
    def get(self):
        templatepath = os.path.dirname(__file__) + '/../templates/'
        html = template.render(templatepath + '01cts_uberheader.html', {'title'})
        html = html + template.render(templatepath + '02cts_uberintroblock_wmodellinks.html', {'model':'analysis','page':'batchinput'})
        html = html + template.render (templatepath + '03cts_ubertext_links_left.html', {})                
        html = html + template.render(templatepath + '04uberbatchinput.html', {
                    'model':'analysis',
                    'model_attributes':'analysis Batch Input'})
        html = html + template.render(templatepath + '04uberbatchinput_jquery.html', {}) 
        html = html + template.render(templatepath + '05cts_ubertext_links_right.html', {})
        html = html + template.render(templatepath + '06cts_uberfooter.html', {'links': ''})
        self.response.out.write(html)

app = webapp.WSGIApplication([('/.*', analysisBatchInputPage)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
    









