# src/genetic_algo_logic/individual_creator.py
import random
from deap import creator, base

# Weights: (-1.0, -1.0, 1.0, 1.0) : minimize cost, minimize latency, maximize availability, maximize mhroughput
try:
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, 1.0, 1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
except RuntimeError:
    pass

#modules-import ?? [NOT]
from src.microservice_catalog import MicroserviceCatalog
from src.scenario_definition import ServiceScenario

def create_random_individual(scenario: ServiceScenario) -> creator.Individual:
    
    #single random service composition based on the scenario's required capabilities = 1 capability slot.
    
    individual_ms_ids = []
    # authentication, storage
    for capability in scenario.required_capabilities:
        # all microservices
        options = scenario.get_options_for_capability(capability)
        if not options:
            raise ValueError(f"Error: No microservice options found for capability '{capability}'. Check data/scenario.")

        # Randomly select one microservice id
        selected_ms = random.choice(options)
        individual_ms_ids.append(selected_ms.id)

    # Return as DEAP Individual type
    return creator.Individual(individual_ms_ids)

def create_population(pop_size: int, scenario: ServiceScenario) -> list[creator.Individual]:
    #initial population of individuals for the GA.
    population = [create_random_individual(scenario) for _ in range(pop_size)]
    return population

if __name__ == "__main__":
    try:
        catalog = MicroserviceCatalog()
        scenario = ServiceScenario(
            name="Test User Service",
            required_capabilities=["user_authentication", "data_storage"],
            catalog=catalog
        )
        test_ind = create_random_individual(scenario)
        print(f"Random Individual created: {test_ind}")

        test_pop = create_population(5, scenario)
        print(f"Population of {len(test_pop)} is created:")
        for ind in test_pop:
            print(f"  - {ind}")

    except Exception as e:
        print(f"Could not run test: {e}.")