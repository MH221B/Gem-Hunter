from itertools import combinations
from copy import deepcopy

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
    variable_values = {}
    for i in range(num_rows):
        for j in range(num_cols):
            variables[(i, j)] = count
            if matrix[i][j] is None:
                variable_values[count] = None
            count += 1
    return variables, variable_values

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

def generateCNFFromConstraintsByCell(cell,matrix, num_rows, num_cols, variables):
    clauses = []
    surrrounding_cells = get_surrounding_cells(matrix, cell, num_rows, num_cols)
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

def printInitialMatrix(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j] if matrix[i][j] is not None else '_', end=' ')
        print()

def checkSolution(matrix, num_rows, num_cols, variables, variable_values):
    if None in variable_values.values():
        return False
    list_numbered_cells = get_numbered_cells(matrix, num_rows, num_cols)
    for cell in list_numbered_cells:
        surrounding_cells = get_surrounding_cells(matrix, cell, num_rows, num_cols)
        count = 0
        for c in surrounding_cells:
            if variable_values[variables[c]] == False:
                count += 1
        if count != matrix[cell[0]][cell[1]]:
            return False
    return True

def assignGuaranteedValues(matrix, num_rows, num_cols, variables, variable_values):
    numbered_cells = get_numbered_cells(matrix, num_rows, num_cols)
    for cell in numbered_cells:
        surrrounding_cells = get_surrounding_cells(matrix, cell, num_rows, num_cols)
        if matrix[cell[0]][cell[1]] == len(surrrounding_cells):
            for c in surrrounding_cells:
                variable_values[variables[c]] = False

def backtrack(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size, index):
    if index == size:
        return checkSolution(matrix, num_rows, num_cols, variables, variable_values)
    variable_values[list_unassigned[index]] = True
    if backtrack(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size, index + 1):
        return True 
    variable_values[list_unassigned[index]] = False
    return backtrack(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size, index + 1)

def solveHelper(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size):
    return backtrack(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size, 0)

def brute_force_solver(matrix, num_rows, num_cols, variables, variable_values):
    assignGuaranteedValues(matrix, num_rows, num_cols, variables, variable_values)
    list_unassigned = []
    for val in variable_values:
        if variable_values[val] == None:
            list_unassigned.append(val)
    size = len(list_unassigned)
    return solveHelper(matrix, num_rows, num_cols, variables, variable_values, list_unassigned, size)
    

def printSolution(matrix, num_rows, num_cols, variables, variable_values):
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is not None:
                print(matrix[i][j], end=' ')
            else:
                if variable_values[variables[(i, j)]] == True:
                    print('G', end=' ')
                else:
                    print('T', end=' ')
        print()

def solutionMatrix(matrix, num_rows, num_cols, variables, variable_values):
    new_matrix = deepcopy(matrix)
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is None:
                if variable_values[variables[(i, j)]]:
                    new_matrix[i][j] = 'G'
                else:
                    new_matrix[i][j] = 'T'
    return new_matrix

def printMatrix(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j], end=' ')
        print()

def main(fileName):
    matrix, num_rows, num_cols = read_matrix_from_file('testcases/' + fileName)
    data = assign_variables(matrix, num_rows, num_cols)
    print("Problem:")
    printInitialMatrix(matrix, num_rows, num_cols)
    print()
    variables = data[0]
    variable_values = data[1]
    checkSolve = brute_force_solver(matrix, num_rows, num_cols, variables, variable_values)
    if checkSolve == True:
        print("Solution:")
        # printSolution(matrix, num_rows, num_cols, variables, variable_values)
        solution = solutionMatrix(matrix, num_rows, num_cols, variables, variable_values)
        printMatrix(solution, num_rows, num_cols)
        return solution
    else:
        print("No solution")
        return None
