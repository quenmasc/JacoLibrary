import math
from Creature import Creature
import numpy as np

class Swarm(object):
    def __init__(self, random, upper_bound, lower_bound, number_of_creatures_main_population,
                 number_of_creatures_auxiliary_population):
        self._upper_bound = upper_bound
        self._lower_bound = lower_bound
        self._number_dimensions = len(self._upper_bound)
        self._random = random
        self._number_of_creatures_main_population = number_of_creatures_main_population
        self._number_of_creatures_auxiliary_population = number_of_creatures_auxiliary_population

        self._array_creatures = self.create_creatures()
        self._array_index_creatures_to_ignore = []

        self._OA = self.generate_OA()

        # Examplar is a list of creatures index of length number of dimensions. If the index of creature 4 appear at
        # position 9 for example. This creature will use the value of the best memory of creature 4 for the
        # position 9
        self._list_examplar_index = self.initialize_examplars()

        self._iterations_since_last_global_best_found = 0
        self._evaluation_number_topology_change = 0

    def create_creatures(self):
        array_creatures = []
        for i in range(self._number_of_creatures_main_population + self._number_of_creatures_auxiliary_population):
            array_creatures.append(Creature(random=self._random,
                                            upper_bound=self._upper_bound, lower_bound=self._lower_bound))
        return array_creatures

    def initialize_examplars(self):
        list_examplar = []
        for creature_index in range(len(self._array_creatures)):
            list_examplar.append(creature_index*np.ones(self._number_dimensions, dtype=int))
        return list_examplar

    def get_worst_creature(self, index_max):
        worst_fitness = -float('Inf')
        worst_index = 0

        index = 0
        for creature in self._array_creatures:
            if index not in self._array_index_creatures_to_ignore:
                if worst_fitness < creature.get_best_memory_fitness():
                    worst_fitness = creature.get_best_memory_fitness()
                    worst_index = index
            index += 1
            if index > index_max:
                break
        return self._array_creatures[worst_index], worst_index

    def get_best_creature_ever(self, get_index=False):
        best_fitness = float('Inf')
        best_index = 0

        index = 0
        for creature in self._array_creatures:
            if best_fitness > creature.get_best_memory_fitness():
                best_fitness = creature.get_best_memory_fitness()
                best_index = index
            index += 1
        if get_index:
            return self._array_creatures[best_index], best_index
        else:
            return self._array_creatures[best_index]

    def run_swarm(self, max_iter, max_evals, fitness_function):
        nmbr_evals = 0.0
        use_fast_convergence_pso = False
        for current_gen in range(max_iter):
            if current_gen % 100 == 0:
                print "CURRENT GEN: ", current_gen
                print "TOTAL EVALS: ", nmbr_evals
                print repr(self.get_best_creature_ever().get_best_memory_fitness())
            evals_done = self.update_swarm(nmbr_evals, max_evals, fitness_function)
            nmbr_evals += evals_done
            if nmbr_evals > max_evals:
                break
            if current_gen % 9 == 0 and current_gen > 10:
                print "  BEST FITNESS: ", \
                      self.get_best_creature_ever().get_best_memory_fitness(), " Number of evaluations so far: ", \
                    nmbr_evals
        best_creature = self.get_best_creature_ever()

        return nmbr_evals, best_creature.get_best_memory_fitness(), best_creature.get_best_memory_position()

    def update_swarm(self, current_number_evaluations, max_evals, fitness_function):
        # Check if we have to remove a creature from the orthogonal learning paradigm:
        if (current_number_evaluations > ((len(self._array_index_creatures_to_ignore)) * max_evals) / (
                    self._number_of_creatures_main_population) and len(self._array_index_creatures_to_ignore) <=
                self._number_of_creatures_main_population):
            self.deactivate_creature(self._number_of_creatures_main_population-1)
            print "Array creatures desactivated : ", self._array_index_creatures_to_ignore
        total_evaluation = 0
        index = 0
        best_creature, best_creature_index = self.get_best_creature_ever(get_index=True)
        best_position = best_creature.get_best_memory_position()
        best_fitness = best_creature.get_best_memory_fitness()
        for creature in self._array_creatures:
            if index not in self._array_index_creatures_to_ignore:
                evals_to_give_creature = current_number_evaluations + total_evaluation
                if index >= self._number_of_creatures_main_population:
                    use_fast_convergence_pso = True
                else:
                    use_fast_convergence_pso = False
                # Check if the creature need a new examplar
                if creature.need_new_examplar():
                    if use_fast_convergence_pso is False:
                        total_evaluation += self.create_new_examplar_main_population(index, fitness_function)
                        creature.new_examplar_created()
                if use_fast_convergence_pso:
                    examplar_for_creature = np.copy(best_position)
                else:
                    examplar_for_creature = self.get_current_examplar(index)
                total_evaluation += creature.update(current_eval=evals_to_give_creature,
                                                    max_evals=max_evals, fitness_function=fitness_function,
                                                    examplar=examplar_for_creature,
                                                    fast_convergence=use_fast_convergence_pso)
                if creature.get_best_memory_fitness() < best_fitness:
                    best_fitness = creature.get_best_memory_fitness()
                    best_position = creature.get_best_memory_position()

            index += 1

        return total_evaluation

    def deactivate_creature(self, index_max):
        # Find the worst creature.
        worst_creature, worst_creature_index = self.get_worst_creature(index_max)
        self._array_index_creatures_to_ignore.append(worst_creature_index)

    def get_examplar_from_array_of_creature_index(self, examplar_index):
        examplar = []
        index = 0
        for creature_to_use_index in examplar_index:
            value_dim = self._array_creatures[int(creature_to_use_index)].get_best_memory_position()[index]
            examplar.append(value_dim)
            index += 1
        return np.array(examplar)

    def get_current_examplar(self, creature_index):
        examplar_index = self._list_examplar_index[creature_index]
        return self.get_examplar_from_array_of_creature_index(examplar_index=examplar_index)

    def get_other_vector_examplar(self, creature_index):
        examplar = np.zeros(self._number_dimensions)
        possible_index = range(self._number_of_creatures_main_population)
        index_to_remove = np.copy(self._array_index_creatures_to_ignore).tolist()
        index_to_remove.append(creature_index)
        for index in sorted(index_to_remove, reverse=True):
            del possible_index[index]
        for i in range(self._number_dimensions):
            # Get two creature randomly
            # Pick two creature at random inside the population (different than the current creature).
            # Check which of those two creature has the best memorized position and use that position
            # at the current dimension for the examplar.
            # Remove the current creature from the possible choice
            if len(possible_index) < 2:
                possible_index = range(self._number_of_creatures_main_population, len(self._array_creatures))
            index_creature_chosen = np.random.choice(possible_index, 2, replace=False)
            if (self._array_creatures[index_creature_chosen[0]].get_best_memory_fitness() <
                    self._array_creatures[index_creature_chosen[1]].get_best_memory_fitness()):
                examplar[i] = index_creature_chosen[0]
            else:
                examplar[i] = index_creature_chosen[1]
        return examplar

    def create_new_examplar_main_population(self, creature_index, fitness_function):
        total_evaluation = 0

        examplar_from_mixed_population_index = self.get_other_vector_examplar(creature_index)
        examplar_from_mixed_population = self.get_examplar_from_array_of_creature_index(
            examplar_from_mixed_population_index)

        array_best_position = [self._array_creatures[creature_index].get_best_memory_position(),
                               examplar_from_mixed_population]
        array_best_position_creature_index = [creature_index, examplar_from_mixed_population_index]
        # Generate positions to test
        array_position_to_test = []
        array_position_creature_index_to_test = []
        for i in range(len(self._OA)):
            position = []
            possible_examplar_index = []
            for j in range(len(self._OA[i])):
                position.append(array_best_position[int(self._OA[i][j])][j])
                if self._OA[i][j] == 1:
                    possible_examplar_index.append(int(array_best_position_creature_index[1][j]))
                else:
                    possible_examplar_index.append(array_best_position_creature_index[0])
            array_position_to_test.append(position)
            array_position_creature_index_to_test.append(possible_examplar_index)
        array_position_to_test = np.array(array_position_to_test)
        fitness_tested_position = []
        for position in array_position_to_test:
            fitness_tested_position.append(fitness_function(position))
            total_evaluation += 1

        fitness_tested_position = np.array(fitness_tested_position)
        # Get the minimum of the tested solution
        best_combination_index = np.argmin(fitness_tested_position)
        best_solution_so_far = array_position_to_test[best_combination_index]

        values_FA = self.evaluate_FA(fitness_tested_position)
        # Get the array of the minimums values
        array_index_minimum_values = np.argmin(values_FA, axis=0)
        # Construct the best combination of level as determined by the FA
        best_solution_by_FA = []
        index_dimension = 0
        best_solution_creature_index_by_FA = []
        for index_creature in array_index_minimum_values:
            best_solution_by_FA.append(array_best_position[index_creature][index_dimension])
            if index_creature == 0:
                best_solution_creature_index_by_FA.append(
                    array_best_position_creature_index[index_creature])
            else:
                best_solution_creature_index_by_FA.append(
                    int(array_best_position_creature_index[index_creature][index_dimension]))
            index_dimension += 1
        # Evaluate this solution
        best_solution_by_FA = np.array(best_solution_by_FA)
        fitness_solution_FA = fitness_function(best_solution_by_FA)
        total_evaluation += 1

        if fitness_solution_FA <= fitness_tested_position[best_combination_index]:
            examplar = best_solution_creature_index_by_FA
            self._list_examplar_index[creature_index] = np.array(examplar, dtype=int)
            return total_evaluation
        else:

            examplar = array_position_creature_index_to_test[best_combination_index]
            self._list_examplar_index[creature_index] = np.array(examplar, dtype=int)
            return total_evaluation

    def evaluate_FA(self, fitness_tested_position):
        # Perform the factor analysis
        values_FA = np.zeros((2, self._number_dimensions))
        for factor in range(self._number_dimensions):
            for level in range(2):
                value_for_element_FA = 0.0
                sum_Zmnq = 0.0
                for experiment in range(len(self._OA)):
                    # Zmnq is the level with the factor and experiment that we're currently testing. It's 0 if we're
                    # not testing it and 1 if we're.
                    if self._OA[experiment][factor] == level:
                        Zmnq = 1.0
                    else:
                        Zmnq = 0.0
                    value_for_element_FA += fitness_tested_position[experiment] * Zmnq
                    sum_Zmnq += Zmnq
                value_for_element_FA /= sum_Zmnq
                values_FA[level][factor] = value_for_element_FA
        return values_FA

    def generate_OA(self):
        # Step 1: Determine M, N and u
        exponent = math.ceil(math.log(self._number_dimensions+1, 2))
        n = int(math.pow(2, exponent))
        OA = np.zeros((n, self._number_dimensions))
        for i in range(1, n+1):
            for j in range(1, self._number_dimensions+1):
                level = 0
                k = j
                mask = n/2.0
                while k > 0:
                    if k % 2 == 1 and self.bitwise_AND(i-1, mask) != 0:
                        level = (level+1) % 2
                    k = math.floor(k/2.0)
                    mask /= 2.0
                OA[i-1][j-1] = level
        return OA

    def bitwise_AND(self, alpha, mask):
        divisor = int(alpha)/int(mask)
        return divisor % 2
