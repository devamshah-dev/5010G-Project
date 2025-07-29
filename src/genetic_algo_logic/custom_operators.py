# src/genetic_algorithm_logic/custom_operators.py
import random
from deap import creator #type hinting Individual
from src.microservice_catalog import MicroserviceCatalog
from src.scenario_definition import ServiceScenario

def mut_swap_microservice(individual: creator.Individual, scenario: ServiceScenario, indpb: float) -> tuple:

    # mutates individual by randomly replacing a microservice in one of its capability slots with another available option for that same capability.
   
    mutated = False
    for i, current_ms_id in enumerate(individual):
        if random.random() < indpb:
            mutated = True
            
            # determine which capability this gene/slot corresponds to assume individual's order matches scenario.required_capabilities order
            try:
                capability = scenario.required_capabilities[i]
            except IndexError:
                #do not happen if individual creation is correct
                print(f"Warning: Individual index {i} out of bounds for scenario capabilities. Skipping mutation.")
                continue
            
            # get all valid microservice options for this specific capability
            options_for_capability = scenario.get_options_for_capability(capability)
            
            # filter out the current microservice = true "swap"
            available_for_swap = [ms.id for ms in options_for_capability if ms.id != current_ms_id]
            
            if available_for_swap:
                # select new random microservice ID from the filtered options
                individual[i] = random.choice(available_for_swap)
                # invalidate fitness so DEAP &needs re-evaluation
                del individual.fitness.values
            else:
                # print(f"No alternative MS found for capability '{capability}'.")
                pass #no swap possible for this gene

    # DEAP return a tuple of the modified individuals.
    return individual,

if __name__ == "__main__":
    try:
        # re-create DEAP types if not already present
        try:
            creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, 1.0, 1.0))
            creator.create("Individual", list, fitness=creator.FitnessMulti)
        except RuntimeError:
            pass

        # mock objects for testing:  imports/instances
        catalog = MicroserviceCatalog()
        scenario = ServiceScenario(
            name="Test Scenario",
            required_capabilities=["user_authentication", "data_storage"], # Example caps
            catalog=catalog
        )

        # sample individual
        sample_individual = creator.Individual(["auth-v1", "db-sql-lite"])
        print(f"Original Individual: {sample_individual}")

        # mutate
        mutated_individual, = mut_swap_microservice(sample_individual, scenario, indpb=1.0) # 100% mutation probability for testing
        print(f"Mutated Individual: {mutated_individual}")
        print(f"Fitness valid after mutation: {mutated_individual.fitness.valid}") # Should be False

    except Exception as e:
        print(f"Could not run test: {e}. Ensure Person 2's modules are in 'src/' and data is present.")