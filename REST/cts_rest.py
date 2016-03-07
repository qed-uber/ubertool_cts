"""
CTS workflow/module-oriented endpoints

For Chemical Editor, p-chem table, chemical speciation,
and reaction pathways.
"""

import logging
import requests
import json
from django.http import HttpResponse, HttpRequest

from chemaxon_cts import jchem_rest
from smilesfilter import filterSMILES
# from models.chemspec.chemspec_model import chemspec as ChemSpec
# from models.chemspec import chemspec_model


# TODO: Consider putting these classes somewhere else, maybe even the *_models.py files!
class Molecule(object):
	"""
	Basic molecule object for CTS
	"""
	def __init__(self):

		# cts keys:
		self.chemical = ''  # initial structure from user (any chemaxon format)
		self.orig_smiles = ''  # before filtering, converted to smiles

		# chemaxon/jchem keys:
		self.smiles = ''  # post filtered smiles 
		self.formula = ''
		self.iupac = ''
		self.mass = ''
		self.structureData = ''

	def createMolecule(self, chemical, orig_smiles, chem_details_response):
		"""
		Gets Molecule attributes from jchem_rest getChemDetails response
		"""
		try:
			# set attrs from jchem data:
			for key in self.__dict__.keys():
				if key != 'orig_smiles' and key != 'chemical':
					self.__setattr__(key, chem_details_response['data'][0][key])
			# set cts attrs:
			self.__setattr__('chemical', chemical)
			self.__setattr__('orig_smiles', orig_smiles)

			return self.__dict__
		except KeyError as err:
			raise err


def getChemicalEditorData(request):
	"""
	Makes call to jchem_rest for chemaxon
	data. Converts incoming structure to smiles,
	then filters smiles, and then retrieves data
	:param request:
	:return: chemical details response json
	"""
	try:
		chemical = request.POST.get('chemical')

		request = requests.Request(data={'chemical': chemical})
		response = jchem_rest.convertToSMILES(request)  # convert chemical to smiles
		response = json.loads(response.content)  # get json data

		orig_smiles = response['structure']
		filtered_smiles = filterSMILES(orig_smiles)  # call CTS REST SMILES filter
		
		request.data = {'chemical': filtered_smiles}
		jchem_response = jchem_rest.getChemDetails(request)  # get chemical details
		jchem_response = json.loads(jchem_response.content)
		
		# return this data in a standardized way for molecular info!!!!
		molecule_obj = Molecule().createMolecule(chemical, orig_smiles, jchem_response)
		
		wrapped_post = {
			'status': True,
			# 'metadata': '',
			'data': molecule_obj
		}
		json_data = json.dumps(wrapped_post)

		return HttpResponse(json_data, content_type='application/json')

	except KeyError as error:
		logging.warning(error)
		wrapped_post = {'status': False, 'error': 'Error validating chemical'}
		return HttpResponse(json.dumps(wrapped_post), content_type='application/json')
	except Exception as error:
		logging.warning(error)
		wrapped_post = {'status': False, 'error': 'Error getting chemical information'}
		return HttpResponse(json.dumps(wrapped_post), content_type='application/json')

# class Metabolite(Molecule):


def getChemicalSpeciationData(request):
	"""
	CTS web service endpoint for getting
	chemical speciation data through  the
	chemspec model/class
	:param request - chemspec_model
	:return: chemical speciation data response json
	"""
	
	# expected inputs (building chemspec model)
	chem_struct = request.POST.get('chem_struct')
	smiles = request.POST.get('smiles')
	orig_smiles = request.POST.get('orig_smiles')
	name = request.POST.get('name')
	formula = request.POST.get('formula')
	mass = request.POST.get('mass')
	get_pka = request.POST.get('get_pka')
	get_taut = request.POST.get('get_taut')
	get_stereo = request.POST.get('get_stereo')
	pKa_decimals = request.POST.get('pKa_decimals')
	pKa_pH_lower = request.POST.get('pKa_pH_lower')
	pKa_pH_upper = request.POST.get('pKa_pH_upper')
	pKa_pH_increment = request.POST.get('pKa_pH_increment')
	pH_microspecies = request.POST.get('pH_microspecies')
	isoelectricPoint_pH_increment = request.POST.get('isoelectricPoint_pH_increment')
	tautomer_maxNoOfStructures = request.POST.get('tautomer_maxNoOfStructures')
	tautomer_pH = request.POST.get('tautomer_pH')
	stereoisomers_maxNoOfStructures = request.POST.get('stereoisomers_maxNoOfStructures')


	try:
		chemspec_obj = ChemSpec(chem_struct, smiles, orig_smiles, name, formula, 
	                    mass, get_pka, get_taut, get_stereo, pKa_decimals, pKa_pH_lower, 
	                    pKa_pH_upper, pKa_pH_increment, pH_microspecies, isoelectricPoint_pH_increment, 
	                    tautomer_maxNoOfStructures, tautomer_maxNoOfStructures, stereoisomers_maxNoOfStructures)

		wrapped_post = {
			'status': True,
			# 'metadata': '',
			'data': chemspec_obj.run_data
		}
		json_data = json.dumps(wrapped_post)

		return HttpResponse(json_data, content_type='application/json')

	except Exception as error:
		logging.warning(error)
		wrapped_post = {'status': False, 'error': 'Error retrieving chemical speciation data'}
		return HttpResponse(json.dumps(wrapped_post), content_type='application/json')




def booleanize(value):
    """
    django checkbox comes back as 'on' or 'off',
    or True/False depending on version, so this
    makes sure they're True/False
    """
    if value == 'on': return True
    if value == 'off': return False