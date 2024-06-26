from pysat.formula import *
from itertools import combinations
from pysat.solvers import Solver

def read_matrix_from_file(file_path):
    matrix = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            row = line.strip().split(',')
            matrix.append([int(x) if x.strip() != '_' else None for x in row])
    num_rows = len(matrix)
    num_cols = len(matrix[0]) if matrix else 0
    return matrix, num_rows, num_cols

# Assign each cell of the matrix a unique variable
def assign_variables(matrix, num_rows, num_cols):
    count = 1
    variables = {}
    for i in range(num_rows):
        for j in range(num_cols):
            variables[(i, j)] = count
            count += 1
    return variables

# Get the neighboring cells of a cell
def get_surrounding_cells(matrix, pos, num_rows, num_cols):
    list_of_cells = []
    for i in range(pos[0] - 1, pos[0] + 2):
        for j in range(pos[1] - 1, pos[1] + 2):
            if i >= 0 and i < num_rows and j >= 0 and j < num_cols and (i, j) != pos and matrix[i][j] is None:
                list_of_cells.append((i, j))
    return list_of_cells

# Get numbered cells
def get_numbered_cells(matrix, num_rows, num_cols):
    list_of_cells = []
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is not None:
                list_of_cells.append((i, j))
    return list_of_cells

#get irrelevant cells
def get_irrelevant_cells(matrix, num_rows, num_cols):
    list_of_cells = []
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is None:
                list_of_cells.append((i, j))
    new_list = list_of_cells.copy()
    for cell in list_of_cells:
        check = True
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if i >= 0 and i < num_rows and j >= 0 and j < num_cols and matrix[i][j] is not None and (i, j) != cell:
                    new_list.remove(cell)
                    check = False
                    break
            if check == False:
                break
    return new_list

def get_list_uninvolved_and_involved_cells_variable(combination, surrounding_cells, variables):
    uninvolved_cells = []
    involved_cells = []
    for cell in surrounding_cells:
        if cell not in combination:
            uninvolved_cells.append(variables[cell])
        else:
            involved_cells.append(variables[cell])
    return uninvolved_cells, involved_cells

def generateCNFFromConstraintsByCell(cell, matrix, num_rows, num_cols, variables):
    clauses = []
    surrrounding_cells = get_surrounding_cells(matrix, cell, num_rows, num_cols)
    # If the number of surrounding cells is equal to the number of the specified cell, then all surrounding cells are traps
    if matrix[cell[0]][cell[1]] == len(surrrounding_cells): 
        for c in surrrounding_cells:
            clauses.append([-variables[c]])
        return clauses
    combination = combinations(surrrounding_cells, matrix[cell[0]][cell[1]])
    for c in combination:
        uninvolved_cells, involved_cells = get_list_uninvolved_and_involved_cells_variable(c, surrrounding_cells, variables)
        for cell in uninvolved_cells:
            sub_clause = []
            sub_clause.append(cell)
            sub_clause.extend(involved_cells)
            sub_clause = sorted(sub_clause)
            if sub_clause not in clauses:
                clauses.append(sub_clause)
        for cell in involved_cells:
            sub_clause = []
            sub_clause.append(-cell)
            sub_clause.extend(-x for x in uninvolved_cells)
            sub_clause = sorted(sub_clause)
            if sub_clause not in clauses:
                clauses.append(sub_clause)
    return clauses

def generateCNFFromConstraints(matrix, num_rows, num_cols, variables):
    clauses = []
    numbered_cells = get_numbered_cells(matrix, num_rows, num_cols)
    for cell in numbered_cells:
        clause = generateCNFFromConstraintsByCell(cell, matrix, num_rows, num_cols, variables)
        clauses.extend(clause)
    irrelevant_cells = get_irrelevant_cells(matrix, num_rows, num_cols)
    for cell in irrelevant_cells:
        clauses.append([variables[cell]])
    clauses = removeDuplicates(clauses)
    return clauses

def removeDuplicates(clauses):
    new_clauses = []
    for clause in clauses:
        if clause not in new_clauses:
            new_clauses.append(clause)
    return new_clauses

# solve CNF formula and return the cells that are traps, cells that are not gems
def solveCNF(clauses, variables):
    solver = Solver()
    for clause in clauses:
        solver.add_clause(clause)
    solver.solve()
    model = solver.get_model()
    if model is None:
        return [], []
    traps = []
    gems = []
    for m in model:
        if m > 0:
            gems.append(m)
        else:
            traps.append(-m)
    return traps, gems

def printCompleteMatrix(matrix, num_rows, num_cols, traps, gems, variables):
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is not None:
                print(matrix[i][j], end=' ')
            else:
                if variables[(i, j)] in traps:
                    print('T', end=' ')
                elif variables[(i, j)] in gems:
                    print('G', end=' ')
        print()

def printInitialMatrix(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j] if matrix[i][j] is not None else '_', end=' ')
        print()

def solutionMatrix(matrix, num_rows, num_cols, traps, gems, variables):
    result = []
    for i in range(num_rows):
        row = []
        for j in range(num_cols):
            if matrix[i][j] is not None:
                row.append(matrix[i][j])
            else:
                if variables[(i, j)] in traps:
                    row.append('T')
                elif variables[(i, j)] in gems:
                    row.append('G')
        result.append(row)
    return result

def printSolution(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j], end=' ')
        print()

def main(fileName):
    matrix, num_rows, num_cols = read_matrix_from_file("testcases/" + fileName)
    print("Problem:")
    printInitialMatrix(matrix, num_rows, num_cols)
    print()
    variables = assign_variables(matrix, num_rows, num_cols)
    clauses = generateCNFFromConstraints(matrix, num_rows, num_cols, variables)
    # print(clauses)
    traps, gems = solveCNF(clauses, variables)
    if not traps and not gems:
        print("No solution")
        return None
    else:
        print("Solution:")
        # printCompleteMatrix(matrix, num_rows, num_cols, traps, gems, variables)
        solution = solutionMatrix(matrix, num_rows, num_cols, traps, gems, variables)
        printSolution(solution, num_rows, num_cols)
    return solution