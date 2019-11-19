\* Cost of Scrap in Steel Grade Recipes *\
Minimize
cost;_to_be_minimized: 88.3333333333 bushlings_wgt
 + 41.6666666667 municipal_shred_wgt + 154.166666667 pig_iron_wgt
 + 71.6666666667 skulls_wgt
Subject To
Cu_constraint: - 0.000145280045032 bushlings_wgt
 + 0.000162997466929 municipal_shred_wgt + 0.000391657754011 skulls_wgt
 <= 0.15
YIELD_constraint: 0.905087073438 bushlings_wgt
 + 0.947526097828 municipal_shred_wgt + 0.944355547647 pig_iron_wgt
 + 0.770452927096 skulls_wgt = 990
Bounds
200 <= bushlings_wgt
100 <= pig_iron_wgt <= 300
End
