from django.views.decorators.http import require_POST
import logging
from . import gentrans_model
import bleach

@require_POST
def gentransOutputPage(request):
    # from cts_app.models.pchemprop import pchemprop_model

    run_type = bleach.clean(request.POST.get('run_type', ''))

    # Chemical Editor tab fields
    chemStruct = bleach.clean(request.POST.get('chem_struct', ''))
    smiles = bleach.clean(request.POST.get('smiles', ''))
    iupac = bleach.clean(request.POST.get('iupac', ''))
    formula = bleach.clean(request.POST.get('formula', ''))
    mass = bleach.clean(request.POST.get('mass', ''))
    orig_smiles = bleach.clean(request.POST.get('orig_smiles', ''))
    exact_mass = bleach.clean(request.POST.get('exactmass', ''))
    cas = bleach.clean(request.POST.get('cas', ''))
    
    # Reaction Pathway Simulator tab fields
    abioticHydrolysis = bleach.clean(request.POST.get('abiotic_hydrolysis', ''))
    abioticRecuction = bleach.clean(request.POST.get('abiotic_reduction', ''))
    mammMetabolism = bleach.clean(request.POST.get('mamm_metabolism', ''))
    photolysis = bleach.clean(request.POST.get('photolysis', ''))
    genLimit = request.POST.get('gen_limit')
    popLimit = request.POST.get('pop_limit')
    likelyLimit = request.POST.get('likely_limit')
    pfas_environmental = bleach.clean(request.POST.get('pfas_environmental', ''))
    pfas_metabolism = bleach.clean(request.POST.get('pfas_metabolism', ''))

    biotrans_metabolism = bleach.clean(request.POST.get('biotrans_metabolism', ''))
    biotrans_libs = bleach.clean(request.POST.get('biotrans_libs', ''))

    envipath_metabolism = bleach.clean(request.POST.get('envipath_metabolism', ''))

    gentrans_obj = gentrans_model.gentrans(run_type, chemStruct, smiles, orig_smiles, iupac, formula, 
                                    mass, exact_mass, cas, abioticHydrolysis, abioticRecuction,
                                    mammMetabolism, photolysis, pfas_environmental, pfas_metabolism,
                                    genLimit, popLimit, likelyLimit, biotrans_metabolism, biotrans_libs, envipath_metabolism)

    return gentrans_obj