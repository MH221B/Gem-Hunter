from pysat.formula import *
from pysat.solvers import Solver

# Define atoms
x, y, z = Atom('x'), Atom('y'), Atom('z')

# Define implication statements
a = Implies(x, y)
b = Implies(y, z)

# Combine atoms to form the conjunction
formula = And(a, b)

# Initialize solver
s = Solver(name='g4')

# Add the formula to the solver
s.add_clause([formula])

# Solve the formula
s.solve()

# Print the model
print(s.get_model())