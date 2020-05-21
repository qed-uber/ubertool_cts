"""
2014-08-13 (np)
"""

# from cts_app.cts_calcs.chemaxon_cts import jchem_rest
# from cts_app.cts_api import cts_rest
import logging
from django.http import HttpRequest
# from cts_app.cts_calcs import data_walks
import datetime
import json

# from cts_app.cts_calcs.calculator import Calculator
from ...cts_calcs.calculator_metabolizer import MetabolizerCalc


class gentrans(object):
    def __init__(self, run_type, chem_struct, smiles, orig_smiles, name, formula, mass,
                 exactMass, cas, abiotic_hydrolysis, abiotic_reduction, mamm_metabolism, photolysis,
                 gen_limit, pop_limit, likely_limit, biotrans_libs):

        self.title = "Generate Transformation Products"
        self.jid = MetabolizerCalc().gen_jid()
        self.run_type = run_type  # single or batch

        # Chemical Structure
        self.chem_struct = chem_struct  # chemical structure
        self.smiles = smiles
        self.orig_smiles = orig_smiles
        # self.iupac = iupac
        self.name = name

        self.formula = formula
        self.mass = '{} g/mol'.format(mass)
        self.exactMass = '{} g/mol'.format(exactMass)
        self.cas = cas

        # Reaction Libraries
        self.abiotic_hydrolysis = abiotic_hydrolysis  # values: on or None
        self.abiotic_reduction = abiotic_reduction
        self.mamm_metabolism = mamm_metabolism
        self.photolysis = photolysis

        self.gen_max = gen_limit
        self.gen_limit = gen_limit  # generation limit
        self.pop_limit = pop_limit  # population limit
        self.likely_limit = likely_limit

        reactionLibs = {
            "hydrolysis": self.abiotic_hydrolysis,
            "abiotic_reduction": self.abiotic_reduction,
            "photolysis": self.photolysis
        }

        self.trans_libs = []
        for key, value in reactionLibs.items():
            if value:
                self.trans_libs.append(key)

        # NOTE: populationLimit is hard-coded to 0 as it currently does nothing
        if biotrans_libs:
            self.metabolizer_request_post = {
                'chemical': self.smiles,
                'gen_limit': self.gen_limit,
                'prop': biotrans_libs
            }
        else:
            self.metabolizer_request_post = {
                'structure': self.smiles,
                'generationLimit': self.gen_limit,
                'populationLimit': 0,
                'likelyLimit': 0.1,
                'excludeCondition': "hasValenceError()"
            }
            if len(self.trans_libs) > 0:
                self.metabolizer_request_post.update({'transformationLibraries': self.trans_libs})

        self.run_data = {
            'title': "Transformation Products Output",
            'jid': self.jid,
            'time': datetime.datetime.strptime(self.jid, '%Y%m%d%H%M%S%f').strftime('%A, %Y-%B-%d %H:%M:%S'),
            'chem_struct': self.chem_struct,
            'smiles': self.smiles,
            'name': self.name,
            'formula': self.formula,
            'mass': self.mass
        }