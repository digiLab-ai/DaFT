import random
import multiprocessing

from deap import algorithms, base, creator, tools

class IndexSelectionGA:
    def __init__(self, n_sub, n_total, fitness_min, **kwargs):
        
        self.n_sub = n_sub
        self.n_total = n_total
        
        self.fitness_min = fitness_min
        
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        
        if kwargs.pop("multiprocessing", True):
            self.toolbox.register("map", multiprocessing.Pool().map)
        
        self.toolbox.register("indices", random.sample, range(self.n_total), self.n_sub)
        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.indices)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.fitness_min)
        
        self.indpb_mate = kwargs.pop("indpb_mate", 0.2)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.indpb_mate)
        
        self.indpb_mutate = kwargs.pop("indpb_mutate", 0.1)
        self.toolbox.register("mutate", tools.mutUniformInt, low=0, up=self.n_total-1, indpb=self.indpb_mutate)
        
        self.tournsize = kwargs.pop("tournsize", 3)
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournsize)
    
    def run(self, **kwargs):
        
        population = self.toolbox.population(n=kwargs.pop("n", 100))
        
        algorithms.eaSimple(population, 
                            self.toolbox, 
                            cxpb=kwargs.pop("cxpb", 0.5), 
                            mutpb=kwargs.pop("mutpb", 0.2), 
                            ngen=kwargs.pop("ngen", 100), 
                            verbose=False)
        
        return tools.selBest(population, k=kwargs.pop("k", 1))
