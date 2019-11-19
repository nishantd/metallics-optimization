import pandas as pd

recipes_wgt1000 = [
                  {"bushling":300, "pig_iron":200, "municipal_shred":300, "skulls":200},
                  {"bushling":290, "pig_iron":210, "municipal_shred":300, "skulls":200},
                  {"bushling":250, "pig_iron":220, "municipal_shred":330, "skulls":200},
                  {"bushling":270, "pig_iron":260, "municipal_shred":270, "skulls":200},
                  {"bushling":220, "pig_iron":190, "municipal_shred":350, "skulls":240},
                  {"bushling":250, "pig_iron":250, "municipal_shred":300, "skulls":200},
                  {"bushling":240, "pig_iron":160, "municipal_shred":340, "skulls":260},
                  {"bushling":230, "pig_iron":270, "municipal_shred":320, "skulls":180},
                  {"bushling":220, "pig_iron":180, "municipal_shred":400, "skulls":200},
                  {"bushling":210, "pig_iron":290, "municipal_shred":380, "skulls":220},
                  ]

recipes_wgt1100 = [
                  {"bushling":310, "pig_iron":240, "municipal_shred":310, "skulls":240},
                  {"bushling":270, "pig_iron":270, "municipal_shred":330, "skulls":230},
                  {"bushling":280, "pig_iron":250, "municipal_shred":360, "skulls":210},
                  {"bushling":270, "pig_iron":260, "municipal_shred":290, "skulls":280},
                  {"bushling":250, "pig_iron":260, "municipal_shred":350, "skulls":240},
                  {"bushling":290, "pig_iron":200, "municipal_shred":360, "skulls":250},
                  {"bushling":240, "pig_iron":210, "municipal_shred":390, "skulls":260},
                  {"bushling":270, "pig_iron":270, "municipal_shred":380, "skulls":180},
                  {"bushling":220, "pig_iron":180, "municipal_shred":450, "skulls":250},
                  {"bushling":280, "pig_iron":190, "municipal_shred":410, "skulls":220},
                  ]

recipes_wgt1200 = [
                  {"bushling":290, "pig_iron":260, "municipal_shred":450, "skulls":200},
                  {"bushling":290, "pig_iron":270, "municipal_shred":420, "skulls":220},
                  {"bushling":380, "pig_iron":250, "municipal_shred":350, "skulls":220},
                  {"bushling":370, "pig_iron":240, "municipal_shred":380, "skulls":210},
                  {"bushling":360, "pig_iron":250, "municipal_shred":360, "skulls":230},
                  {"bushling":350, "pig_iron":270, "municipal_shred":350, "skulls":240},
                  {"bushling":300, "pig_iron":270, "municipal_shred":380, "skulls":250},
                  {"bushling":290, "pig_iron":280, "municipal_shred":390, "skulls":240},
                  {"bushling":290, "pig_iron":220, "municipal_shred":410, "skulls":280},
                  {"bushling":310, "pig_iron":190, "municipal_shred":450, "skulls":250},
                  ]

def create_recipe(recipes_wgt1000,recipes_wgt1100, recipes_wgt1200 ):
    recipe_list = pd.DataFrame({'recipes_wgt1000': recipes_wgt1000, 'recipes_wgt1100': recipes_wgt1100,
                            'recipes_wgt1200': recipes_wgt1200, }, columns=['recipes_wgt1000', 'recipes_wgt1100', 'recipes_wgt1200'])
    return recipe_list
