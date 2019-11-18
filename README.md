# The hackathon

- Each team must produce recipes for the production schedule of heats (given in data/?/production_schedule.json).

- The final output must be in the same format as given in data/final_output_example.json. The fields are self explanatory.

- The only data available is under the data directory as described in data/README. Please read this file carefully.

- Optimization for the recipes:
  - The only thing being optimized for is scrap cost. We assume there are no other costs.
  
- Try to create a solution that at the high level might resemble the actual metallics solution in terms of the components. I.e. Models for Copper and yield estimation, the optimizer that creates recipes and uses the models (or api's to the models) to create recipes, etc.

## Teams

- Team 1: Nishant, Max, Ibrahim
- Team 2: Rohan, Dehong, Simon
- Team 3: Ajay, Rashmi, Ashish
- Team 4: Shyam, Evgenii, Philipp
- Team 5: Ying, Sebastian, Lena

### Constraints:
- See constraints.json in every dataset. They are self-explanatory and minimal.

### Copper model:
The only tramp element being measured and specified in the production schedule is Copper (cu). The only data you have to create a copper model is the history of previous heats (data/?/previous_heats_with_properties.json). (See data/README.md for more.)

## Rules

- No existing Noodle or SMS code can be used. Assume everything in this repo is public.

- GIT policies:
  - NO CHECKINS into the master branch.
  - Create a branch for your team. I.e. team-funny-geeks. Use this as your teams 'master'.
  - For your own work, if you want to push additional branches to the repo, create branches with your name (i.e. nishant-create-cost-estimator). 

- There must be a file generate_recipes.py that can be run with a single parameter (the name of the data directory i.e. data/1/ or data/2/ etc) and should output on stdout valid json for the schedule with recipes (see data/final_output_example.json). For example
```
python generate_recipes.py data/1/ > 1_results.json
```
Should result in a valid scrap recipe schedule in 1_results.json.

- Work with your teams not across teams (i.e. within Noodle or SMS) for the duration of the hackathon in the spirit of the hackathon.

- You can use any public libraries and tools. They should be pip installable (add them to your requirements.txt).


## Helpful suggestions

- Make any assumptions you want in the interests of getting something done. If you can't get something done, create the simplest (or simplistic) solution, document it as 'to be improved' and move on. If something is not clear, add your assumptions and move forward.

- Create a python virtual environment and keep a requirements.txt file so everyone in your team can run the code.

- Use python3 (in case someone is still on 2.7)

- Work from the outside in. Get something working end to end with the API / function calls and function signatures first (mock the returned data) and then work on implementation.

- Any schedule with recipes (i.e. a greedy schedule vs optimal) is better than no schedule.

- Git strategies:
  - Use the merge vs rebase git technique. I.e. git fetch, git merge.
  
 
## First steps for each team

- (everyone) Send Nishant your github account name so you can become a collaborator on this repo.
- Decide on the team name.
- Create a branch that will be your teams 'master'. (team-super-cool-dudes). Make sure everyone can check something into this branch.
- Go.

## What else?

Everything else goes. If you have someone interested in creating a UI that shows the schedule or triggers a recalculation of the recipes for a schedule, feel free.

## Afterwards

We want to know

- How you collaborated.
- What was your high level 'architecture' of the system.
- What you learnt about the problem.
- What was emphasised in your solution.
- Anything else you want to contribute and take forward as we build the actual system.
