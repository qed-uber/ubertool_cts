# -*- coding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE']='settings'
import webapp2 as webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class pchempropOutputPage(webapp.RequestHandler):
    def post(self):
        templatepath = os.path.dirname(__file__) + '/../templates/'
        html = template.render(templatepath + '01cts_uberheader.html', {'title'})
        html = html + template.render(templatepath + '02cts_uberintroblock_wmodellinks.html',  {'model':'pchemprop','page':'output'})
        html = html + template.render (templatepath + '03cts_ubertext_links_left.html', {})                               
        html = html + template.render(templatepath + '04uberoutput_start.html', {
                'model':'pchemprop', 
                'model_attributes':'pchemprop Output'})
        html = html + """
        <table width="600" border="1">
          
        </table>
        <p>&nbsp;</p>                     
        
        <table width="600" border="1">
        
        </table>
        """
        html = html + template.render(templatepath + '04uberoutput_end.html', {})
        html = html + template.render(templatepath + '06cts_uberfooter.html', {'links': ''})
        self.response.out.write(html)

app = webapp.WSGIApplication([('/.*', pchempropOutputPage)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()

 

    