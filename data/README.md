# Information about the files

## production_schedule.json:

The heats for which recipes are required. The chemistry specification contains the maximum allowable percent of tramp elements. In this dataset, the only tramp element we are concerned about is cu (copper).

## scrap_inventory[123].json:

The current scrap inventory that can be used. There are three different datasets with different levels of inventory to test your solution with.

## previous_heats_with_properties.json:

This is a history of previous heats. The columns are as below.
tap_weight: The weight of the molten metal that resulted from the heat. (There is no heel - only slag and tap).
chemistry: The measured chemistry of the molten metal. (In this case only cu).
actual_recipe: The actual weights of the commodities used in this heat. This is not the intended weights.

## scrap_orders.json:

Orders for scrap. Note that the total of the orders may not equal the inventory. These are the available orders. There may have been more orders that we don't have access to, so inventory could be more or less than the totals in these orders. These orders should be used to get scrap price for optimization.

## final_output_example.json

Example of the final output.
The predicted fields are your predications.
The suggested_recipe is your suggested recipe for this heat.

