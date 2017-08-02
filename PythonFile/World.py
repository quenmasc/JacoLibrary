from Swarm import Swarm
import FitnessFunction
import numpy as np

class World(object):
    '''
        lower_bound and upper_bound refer to the min and max of the function to optimize respectively.
        number_of_genes correspond to the number of dimensions of the function to optimize.
        population_size Number of creature in a population
        number_of_generation correspond to the number of the main loop the algorithm will do
    '''
    def __init__(self, lower_bound, upper_bound, swarm_size_main_population, swarm_size_auxiliary_population,
                 fitness_function, swarm_confidence=2.0):
        self._random = np.random.RandomState()
        self._number_of_dimensions = number_of_dimensions
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._number_of_generation_swarm = number_of_generation_swarm
        self._swarm_size_main_population = swarm_size_main_population
        self._swarm_size_auxiliary_population = swarm_size_auxiliary_population

        #Swarm hyper-parameters
        self._swarm_confidence = swarm_confidence

        self._fitness_function = fitness_function

        # Create the main swarm responsible to explore the function
        self._swarm = Swarm(number_of_creatures_main_population=self._swarm_size_main_population,
                            number_of_creatures_auxiliary_population=self._swarm_size_auxiliary_population,
                            lower_bound=self._lower_bound, upper_bound=self._upper_bound, random=self._random)

        self._list_real_evaluation_position = []
        self._list_real_evaluation_fitness = []

    def run_world(self, max_evals):
        nmbr_evals, best_creature_fitness, best_creature_position = self._swarm.run_swarm(
            max_iter=self._number_of_generation_swarm, fitness_function=self._fitness_function, max_evals=max_evals)
        print "FINISHED"
        print "BEST POSITION FOUND"
        print best_creature_fitness
        print best_creature_position
        return nmbr_evals, best_creature_fitness, best_creature_position

dimensions = [100]
all_the_positions_with_curiosity = []
nmbr_repetition = 30
all_the_fitness_with_curiosity = np.zeros(nmbr_repetition)
swarm_size_main_population = 120
swarm_size_auxiliary_population = 40
number_of_evals = 500000


for repeat in range(nmbr_repetition):
    print "Schwefel"
    i = 0
    for number_of_dimensions in dimensions:
        # Schwefel
        lower_bound = - 500.*np.ones(number_of_dimensions)
        upper_bound = 500.*np.ones(number_of_dimensions)
        number_of_generation_swarm = 10000
        swarmProcess = World(lower_bound=lower_bound, upper_bound=upper_bound,
                             swarm_size_main_population=swarm_size_main_population,
                             swarm_size_auxiliary_population=swarm_size_auxiliary_population,
                             fitness_function=FitnessFunction.schwefel_function)
        nmbr_evals, best_creature_fitness, best_creature_position = swarmProcess.run_world(number_of_evals)
        print "FINAL FITNESS FOUND: ", best_creature_fitness
        all_the_fitness_with_curiosity[repeat] = best_creature_fitness
        if repeat == 0:
            all_the_positions_with_curiosity.append(best_creature_position)
        print "TOTAL NUMBER EVALUATION: ", nmbr_evals
        i += 1

print "Average value found:"
print "AVERAGE: ", np.mean(all_the_fitness_with_curiosity), \
    " STD: ", np.std(all_the_fitness_with_curiosity)
print all_the_fitness_with_curiosity
f = open('result_100D', 'a')
f.write("Schwefel (100D):\n")
f.write("TAD-PSO:\n")
f.write(str(all_the_fitness_with_curiosity)+'\n')
f.write('AVERAGE: '+str(np.mean(all_the_fitness_with_curiosity))+'\n STD: '+str(np.std(all_the_fitness_with_curiosity)))
f.write('\n\n\n')
f.close()
