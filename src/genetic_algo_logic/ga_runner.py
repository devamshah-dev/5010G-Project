# src/ga_logic/genetic_algorithm_runner.py
import random
from deap import base, tools

# Import your custom modules
from src.genetic_algo_logic.individual_creator import creator, create_population # Import creator here!
from src.genetic_algo_logic.custom_operators import mut_swap_microservice # If you use your custom mutation

# Import Person 2's modules (these will be available after your first merge)
from src.composition_simulator import CompositionSimulator
from src.microservice_catalog import MicroserviceCatalog
from src.scenario_definition import ServiceScenario

class MOGA_Runner:
    """
    Orchestrates the Multi-Objective Genetic Algorithm for service composition.
    """
    def __init__(self, scenario: ServiceScenario, simulator: CompositionSimulator):
        self.scenario = scenario
        self.simulator = simulator
        self.toolbox = base.Toolbox()
        self._setup_toolbox()

    def _setup_toolbox(self):
        """
        Configures the DEAP toolbox with genetic operators:
        individual creation, fitness evaluation, selection, crossover, and mutation.
        """
        # 1. Individual and Population Creation
        self.toolbox.register("individual_creator", create_population, scenario=self.scenario)
        self.toolbox.register("population", self.toolbox.individual_creator) # Wrapper for DEAP's initRepeat

        # 2. Fitness Evaluation (CRITICAL LINK TO PERSON 2's SIMULATOR)
        self.toolbox.register("evaluate", self._evaluate_composition)

        # 3. Genetic Operators
        # Selection: NSGA-II is widely used for multi-objective problems
        self.toolbox.register("select", tools.selNSGA2)

        # Crossover: Combines two individuals (e.g., swapping segments of their MS IDs lists)
        self.toolbox.register("mate", tools.cxTwoPoint) # Example: Two-point crossover for lists

        # Mutation: Randomly alters an individual (e.g., swapping a MS for another valid one)
        # Using your custom mutation:
        self.toolbox.register("mutate", mut_swap_microservice, scenario=self.scenario, indpb=0.1)
        # Or a DEAP built-in, e.g., tools.mutShuffleIndexes:
        # self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1) # Shuffles elements within the list

    def _evaluate_composition(self, individual: creator.Individual) -> tuple:
        """
        Evaluates a service composition (individual) by calling Person 2's simulator.
        The simulator returns a dictionary of metrics, which are then mapped to a tuple
        in the exact order expected by `creator.FitnessMulti`'s weights.
        """
        ms_ids = list(individual) # Ensure individual is treated as a list of IDs
        
        # --- THIS IS THE CALL TO PERSON 2'S SIMULATOR ---
        metrics = self.simulator.calculate_composite_metrics(ms_ids)

        # Validate that required metrics are present
        required_metrics = ['total_cost', 'total_latency_ms', 'total_availability_percent', 'min_throughput_rps']
        if not all(k in metrics for k in required_metrics):
            print(f"Warning: Simulator did not return all required metrics for {ms_ids}. Got: {metrics}")
            # Assign worst-case fitness if metrics are missing to penalize invalid individuals
            return float('inf'), float('inf'), 0.0, 0.0

        # IMPORTANT: The order of values in this tuple MUST match the weights in individual_creator.py
        # weights=(-1.0, -1.0, 1.0, 1.0) -> (cost, latency, availability, throughput)
        return (metrics['total_cost'],
                metrics['total_latency_ms'],
                metrics['total_availability_percent'],
                metrics['min_throughput_rps'])

    def run(self, pop_size: int = 100, num_generations: int = 50, cx_prob: float = 0.7, mut_prob: float = 0.2) -> tools.ParetoFront:
        """
        Runs the main Multi-Objective Genetic Algorithm loop.

        Args:
            pop_size: Number of individuals in the population.
            num_generations: Number of generations to evolve.
            cx_prob: Probability of crossover operation.
            mut_prob: Probability of mutation operation.

        Returns:
            A DEAP ParetoFront object containing the non-dominated solutions.
        """
        print(f"--- Starting GA Evolution ---")
        print(f"Population Size: {pop_size}, Generations: {num_generations}")
        print(f"Crossover Prob: {cx_prob}, Mutation Prob: {mut_prob}")

        # Initialize the population
        population = self.toolbox.population(n=pop_size) # Using toolbox.population for convenience

        # Evaluate the initial population
        # map() applies evaluate to each individual; results are assigned to individual.fitness.values
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Keep track of the best (non-dominated) solutions found so far
        # ParetoFront automatically handles non-dominated solutions
        hall_of_fame = tools.ParetoFront()
        hall_of_fame.update(population)

        # Main evolutionary loop
        for gen in range(1, num_generations + 1):
            # Select the next generation individuals (using NSGA-II)
            # The 'select' operator returns a new list of individuals, which are clones
            # of the fittest ones from the current population.
            offspring = self.toolbox.select(population, len(population))
            
            # Clone the selected individuals to ensure operations affect new instances
            offspring = list(map(self.toolbox.clone, offspring))

            # Apply crossover on the offspring
            # Iterate over pairs of individuals (every other one)
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < cx_prob:
                    self.toolbox.mate(child1, child2)
                    # Invalidate fitness values of modified children
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation on the offspring
            for mutant in offspring:
                if random.random() < mut_prob:
                    self.toolbox.mutate(mutant)
                    # Invalidate fitness value of the mutated individual
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness (i.e., new or modified ones)
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Replace the old population by the offspring
            population[:] = offspring
            
            # Update the Pareto front with the current population's non-dominated solutions
            hall_of_fame.update(population)

            # Log progress
            if gen % 10 == 0 or gen == num_generations:
                print(f"  Gen {gen}/{num_generations} | Pop Size: {len(population)} | Pareto Front Size: {len(hall_of_fame)}")
                
        print("--- GA Evolution Complete ---")
        return hall_of_fame # Return the collection of non-dominated solutions