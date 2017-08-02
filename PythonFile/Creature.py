import numpy as np
import math


class Creature(object):
    def __init__(self, random, upper_bound, lower_bound, swarm_confidence=2.0, position=None,
                 fitness=float('Inf')):
        self._upper_bound = np.array(upper_bound, dtype='float64')
        self._lower_bound = np.array(lower_bound, dtype='float64')
        # Array containing the min and max possible for each position
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        # Get the length of each bound
        bound_distance = []
        for i in range(len(self._lower_bound)):
            bound_distance.append(self._upper_bound[i] - self._lower_bound[i])
        self._bound_distance = np.array(bound_distance)


        self._number_dimensions = len(self._upper_bound)
        self._random = random

        self._fitness = fitness
        if position is None:
            self._position = np.array(self.generate_vector_random(), dtype='float64')
        else:
            self._position = np.array(position, dtype='float64')
        self._velocity = np.array(self.generate_vector_random(), dtype='float64')
        self._max_velocity = .5*self._bound_distance

        self._best_memory_fitness = self._fitness
        self._best_memory_position = np.copy(self._position)

        self._refreshing_gap = 5
        self._stall_iteration = self._refreshing_gap+1

        self._max_weight_velocity = .9
        self._min_weight_velocity = .4

        self._swarm_confidence = swarm_confidence

        self._got_reset = False

        self._current_examplar = np.copy(self._best_memory_position)
        self._growth_weight_velocity = 1.

    # Generate the position or the velocity of the creature randomly
    def generate_vector_random(self):
        return (self._random.uniform(size=self._number_dimensions) *
                (self._upper_bound - self._lower_bound)) + self._lower_bound

    def get_best_memory_fitness(self):
        return self._best_memory_fitness

    def get_best_memory_position(self):
        return np.copy(self._best_memory_position)

    def get_position(self):
        position = []
        for i in range(len(self._position)):
            position.append(self._best_memory_position[i])
        return np.array(position)

    def get_velocity(self):
        return np.copy(self._velocity)

    def set_random_velocity_except_for_this_dimension(self, index_dimension_to_keep):
        random_vector = self.generate_vector_random()
        self._velocity = np.array(random_vector)
        self._velocity[index_dimension_to_keep] = 1.

    def need_new_examplar(self):
        return self._stall_iteration > self._refreshing_gap

    def new_examplar_created(self):
        self._stall_iteration = 0

    def update_velocity(self, current_gen, max_iter, examplar=None, fast_convergence=False):
        weight_velocity = self._max_weight_velocity - (((self._max_weight_velocity - self._min_weight_velocity) *
                                                        current_gen) / float(max_iter))

        inertia = weight_velocity * self._velocity

        if fast_convergence:

            c1 = (.5 - 2.5) * float(current_gen) / float(max_iter) + 2.5
            cognitive_component = np.ones(self._number_dimensions)
            for i in range(self._number_dimensions):
                cognitive_component[i] = c1 * self._random.uniform() * (self._best_memory_position[i] -
                                                                        self._position[i])

            c2 = (2.5 - .5) * float(current_gen) / float(max_iter) + .5
            social_component = np.ones(self._number_dimensions)
            for i in range(self._number_dimensions):
                social_component[i] = c2 * self._random.uniform() * (examplar[i] - self._position[i])
            velocity = inertia + np.copy(cognitive_component) + np.copy(social_component)
            for i in range(len(velocity)):
                velocity[i] = cmp(velocity[i], 0.0) * min(abs(self._max_velocity[i]), abs(velocity[i]))
        else:
            random_value = self._random.rand()

            if examplar is None:
                swarm_influence = np.array(self._swarm_confidence * random_value *
                                           (np.array(self._current_examplar, dtype='float64') -
                                            np.array(self._position, dtype='float64')))
            else:
                swarm_influence = np.array(self._swarm_confidence*random_value *
                                           (np.array(examplar, dtype='float64')-np.array(self._position, dtype='float64')))
                self._current_examplar = np.copy(examplar)
            velocity = inertia + swarm_influence

            for i in range(len(velocity)):
                if abs(velocity[i]) > self._max_velocity[i]:
                    velocity[i] = cmp(velocity[i], 0.0)*self._max_velocity[i]
        self._velocity = velocity

    def update_position(self):
        self._position += np.copy(self._velocity)

    def update_fitness(self, fitness_function):
        for xi, upper_bound_i, lower_bound_i in zip(self._position, self._upper_bound, self._lower_bound):
            # Check if the creature is outside the search space. If yes, do not evaluate. If no, proceed normally.
            if xi > upper_bound_i or xi < lower_bound_i:
                return 0
        self._fitness = fitness_function(self._position)
        if self._fitness < self._best_memory_fitness:
            self._stall_iteration = 0
            self._best_memory_fitness = self._fitness
            new_best_position = []
            for i in self._position:
                new_best_position.append(i)
            self._best_memory_position = np.array(new_best_position)
        else:
            self._stall_iteration += 1

        return 1

    def update(self, current_eval, max_evals, fitness_function, examplar, fast_convergence):
        self._current_examplar = np.copy(examplar)
        self.update_velocity(current_eval, max_evals, examplar, fast_convergence)
        self.update_position()
        return self.update_fitness(fitness_function=fitness_function)
