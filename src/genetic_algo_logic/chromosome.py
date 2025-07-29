# genetic_algo_logic/chromosome.py
#simple list of strings/complex object
class ServiceComposition:
    def __init__(self, microservice_ids: list[str]):
        self.microservice_ids = microservice_ids
        self.fitness = None # cost, latency, availability,
        self.objectives = {} # stores the calculated objectives

    def __repr__(self):
        return f"Composition({self.microservice_ids}, Fitness={self.fitness})"

    # You might need methods here for mutation/crossover specific logic if not using DEAP's defaults