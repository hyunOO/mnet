import random
from deap import base, creator, tools

# Now hardcoded, but later it will be replaced with data from the outside
variables = ['x', 'y', 'z']
# Now hardcoded, but later it will be replaced with data from the outside
branches = ['x + y + 2*z > 6', 'x < 10', 'y > 3', 'z < 1', 'x + y + z < 9']

IND_SIZE = len(variables)

def normalize(bd):
	return 1 - pow(1.001, -bd)

def is_pass(ind, branch):
	for i in range(len(ind)):
		exec("%s = %s" % (variables[i], ind[i]))
	if eval(branch):
		return True
	else:
		return False

def branch_distance(individual, branch):
	for i in range(len(individual)):
		exec("%s = %s" % (variables[i], individual[i]))
	if '>' in branch:
		branch_elem = branch.split('>')
		return eval(branch_elem[1] + ' - (' + branch_elem[0] + ')')
	elif '>=' in branch:
		branch_elem = branch.split('>=')
		return eval(branch_elem[1] + ' - (' + branch_elem[0] + ')')
	elif '<' in branch:
		branch_elem = branch.split('<')
		return eval(branch_elem[0] + ' - (' + branch_elem[1] + ')')
	elif '<=' in branch:
		branch_elem = branch.split('<=')
		return eval(branch_elem[0] + ' - (' + branch_elem[1] + ')')
	elif '==' in branch:
		branch_elem = branch.split('==')
		return abs(eval(branch_elem[0] + ' - (' + branch_elem[1] + ')'))
	elif '!=' in branch:
		branch_elem = branch.split('!=')
		return -abs(eval(branch_elem[0] + ' - (' + branch_elem[1] + ')'))
	else:
		return 0

def generate_fitness(individual, *fitness_func):
	count = 0
	fitness_lst = []
	for i, fitness in enumerate(fitness_func):
		count += 1
		fitness_lst.append(fitness)	

	for i in range(len(individual)):
		exec("%s = %s" % (variables[i], individual[i]))
	approach_lv = len(branches) - 1
	for i in branches:
		if eval(i):
			approach_lv -= 1
		else:
			return [approach_lv + normalize(branch_distance(individual, i))] + [fit(individual) for fit in fitness_lst]
	return [0] * (count + 1)

def run(toolbox):
	pop = toolbox.population(n=200)
	CXPB, MUTPB, NGEN = 0.5, 0.2, 50
	# Evaluate the entire population
	fitnesses = map(toolbox.evaluate, pop)
	for ind, fit in zip(pop, fitnesses):
		ind.fitness.values = fit

	for g in range(NGEN):
		print(g)
		# Select the next generation individual
		offspring = toolbox.select(pop, len(pop)//2)
		# Clone the selected individual
		offspring = list(map(toolbox.clone, offspring))
		# Apply crossover to each pair
		new_offspring = []
		for child1, child2 in zip(offspring[::2], offspring[1::2]):
			toolbox.mate(child1, child2)
			new_offspring.append(child1)
			new_offspring.append(child2)
		# Apply mutation to each offspring
		for mutant in offspring:
			if random.random() < MUTPB:
				toolbox.mutate(mutant)
				del mutant.fitness.values
		# Apply mutation to each new_offspring
		for mutant in new_offspring:
			if random.random() < MUTPB:
				toolbox.mutate(mutant)
				del mutant.fitness.values
		# Make individuals for the next generation
		next_gen = offspring + new_offspring
		fitnesses = map(toolbox.evaluate, next_gen)
		for ind, fit in zip(next_gen, fitnesses):
			print(fit)
			ind.fitness.values = fit
			if fit[0] == 0:
				return ind
		# The population is entirely replaced by the next_gen
		pop[:] = next_gen
	
	return pop[0], pop[0].fitness.values

def toolbox_initialize(objectives_no):
	creator.create("FitnessMin", base.Fitness, weights=[-1.0]*objectives_no)
	creator.create("Individual", list, fitness=creator.FitnessMin)

	toolbox = base.Toolbox()
	toolbox.register("attribute", random.random)
	toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("mate", tools.cxTwoPoints)
	toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
	return toolbox

def run_ga(fitness):
	toolbox = toolbox_initialize(1)
	toolbox.register("evaluate", fitness)
	toolbox.register("select", tools.selTournament, tournsize=3)
	run(toolbox)
	
def run_nsga(fitness):
	toolbox = toolbox_initialize(2)
	toolbox.register("evaluate", fitness)
	toolbox.register("select", tools.selNSGA2)
	run(toolbox)

