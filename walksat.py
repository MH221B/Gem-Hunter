from itertools import combinations
from copy import deepcopy
from random import choice
from random import random
import time

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
        return clauses, True
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
    return clauses, False

def generateCNFFromConstraints(matrix, num_rows, num_cols, variables, unit_clauses=[]):
    clauses = []
    numbered_cells = get_numbered_cells(matrix, num_rows, num_cols)
    for cell in numbered_cells:
        clause = generateCNFFromConstraintsByCell(cell, matrix, num_rows, num_cols, variables)
        if clause[1] == True:
            unit_clauses.extend(deepcopy(clause[0]))
        clauses.extend(clause[0])
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

def removeLiteral(clause, literal):
    if literal in clause:
        return True
    if -literal in clause:
        clause.remove(-literal)
    return clause

def removeLiteralFromClauses(clauses, literal):
    new_clauses = []
    for clause in clauses:
        copied_clause = deepcopy(clause)
        new_clause = removeLiteral(copied_clause, literal)
        if new_clause != True:
            new_clauses.append(new_clause)
    return new_clauses

def checkSolve(clauses, variable_values):
    new_clauses = deepcopy(clauses)
    for val in variable_values:
        if variable_values[val] == True:
            new_clauses = removeLiteralFromClauses(new_clauses, val)
        else:
            new_clauses = removeLiteralFromClauses(new_clauses, -val)
    if not new_clauses:
        return True
    if [] in new_clauses:
        return False

def getFalseClauses(clauses, variable_values):
    false_clauses = []
    for clause in clauses:
        check = False
        for literal in clause:
            if literal > 0 and variable_values[literal] == True:
                check = True
                break
            if literal < 0 and variable_values[-literal] == False:
                check = True
                break
        if not check:
            false_clauses.append(clause)
    return false_clauses

def computeBreakCount(clauses, variable_values, literal):
    break_count = 0
    for clause in clauses:
        if literal in clause:
            if len(clause) == 1:
                if variable_values[abs(literal)] == False:
                    break_count += 1
        elif -literal in clause:
            if len(clause) == 1:
                if variable_values[abs(literal)] == True:
                    break_count += 1
    return break_count

def walkSAT(clauses, variable_values, p):
    while checkSolve(clauses, variable_values) == False:
        false_clauses = getFalseClauses(clauses, variable_values)
        clause = choice(false_clauses)
        check = False
        for literal in clause:
            break_count = computeBreakCount(clauses, variable_values, abs(literal))
            if break_count == 0:
                variable_values[abs(literal)] = not variable_values[abs(literal)]
                check = True
                break
        if check == False:
            if random() < p:
                literal = choice(clause)
            else:
                literal = min(clause, key=lambda x: computeBreakCount(clauses, variable_values, abs(x)))
            variable_values[abs(literal)] = not variable_values[abs(literal)]

def printInitialMatrix(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j] if matrix[i][j] is not None else '_', end=' ')
        print()

def printSolution(matrix, num_rows, num_cols, variables, variable_values):
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is not None:
                print(matrix[i][j], end=' ')
            else:
                print('G' if variable_values[variables[(i, j)]] else 'T', end=' ')
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

def updateVariableValues(variable_values, dict_unassigned):
    for val in dict_unassigned:
        variable_values[val] = dict_unassigned[val]

if __name__ == "__main__":
    matrix, num_rows, num_cols = read_matrix_from_file('testcases/input4.txt')
    data = assign_variables(matrix, num_rows, num_cols)
    print("Problem:")
    printInitialMatrix(matrix, num_rows, num_cols)
    print()
    variables = data[0]
    variable_values = data[1]
    unit_clause = []
    clauses = generateCNFFromConstraints(matrix, num_rows, num_cols, variables, unit_clause)
    unit_clause = removeDuplicates(unit_clause)
    for i in range(len(unit_clause)):
        variable_values[abs(unit_clause[i][0])] = False
    for i in range(len(unit_clause)):
        clauses = removeLiteralFromClauses(clauses, unit_clause[i][0])
    dict_unassigned = {}
    for val in variable_values:
        if variable_values[val] == None:
            dict_unassigned[val] = True
    start = time.time()
    walkSAT(clauses, dict_unassigned, 0.5)
    end = time.time()
    print("Solution:")
    updateVariableValues(variable_values, dict_unassigned)
    printSolution(matrix, num_rows, num_cols, variables, variable_values)
    print("Time:", end - start, "s")
    