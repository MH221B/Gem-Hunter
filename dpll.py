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

def printInitialMatrix(matrix, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            print(matrix[i][j] if matrix[i][j] is not None else '_', end=' ')
        print()

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

def calcOccuringLiteralInMinClauses(value, min_clauses):
    count = 0
    for clause in min_clauses:
        if value in clause:
            count += 1
    return count

def getMostOccuringLiteral(min_clauses, val):
    count = 0
    res = None
    for value in val:
        if calcOccuringLiteralInMinClauses(value, min_clauses) > count:
            count = calcOccuringLiteralInMinClauses(value, min_clauses)
            res = value
    return res

def chooseLiteral(clauses, unit_clauses=[]):
    if clauses:
        if unit_clauses != []:
            res = unit_clauses[0][0]
            print(f"Choose unit clause: {res}")
            unit_clauses.pop(0)
            return res
        else:
            min_len = len(clauses[0])
            for i in range(1, len(clauses)):
                if len(clauses[i]) < min_len:
                    min_len = len(clauses[i])
            val = []
            min_clauses = []
            for clause in clauses:
                if len(clause) == min_len:
                    min_clauses.append(clause)
                    for value in clause:
                        if value not in val:
                            val.append(value)
            res = getMostOccuringLiteral(min_clauses, val)
            print(f"Choose most occuring literal in min clauses: {res}")
            return res
    return None

def DPLL(clauses, literal=None, variable_values={}, unit_clauses=[]):
    if literal != None:
        variable_values[abs(literal)] = True if literal > 0 else False
        new_clauses = removeLiteralFromClauses(clauses, literal)
    else:
        new_clauses = clauses
    if not new_clauses:
        return True
    if [] in new_clauses:
        return False
    new_literal = chooseLiteral(new_clauses, unit_clauses)
    if new_literal:
        if DPLL(new_clauses, -new_literal, variable_values, unit_clauses):
            return True
        return DPLL(new_clauses, new_literal, variable_values, unit_clauses)
    return True

def printSolution(matrix, num_rows, num_cols, variables, variable_values):
    for i in range(num_rows):
        for j in range(num_cols):
            if matrix[i][j] is not None:
                print(matrix[i][j], end=' ')
            else:
                print('G' if variable_values[variables[(i, j)]] else 'T', end=' ')
        print()

if __name__ == "__main__":
    matrix, num_rows, num_cols = read_matrix_from_file('testcases/11x11.txt')
    data = assign_variables(matrix, num_rows, num_cols)
    variables = data[0]
    variable_values = data[1]
    unit_clause = []
    clauses = generateCNFFromConstraints(matrix, num_rows, num_cols, variables, unit_clause)
    unit_clause = removeDuplicates(unit_clause)
    print(unit_clause)
    check = DPLL(clauses, variable_values = variable_values, unit_clauses = unit_clause)
    print("Problem:")
    printInitialMatrix(matrix, num_rows, num_cols)
    print()
    print("Solution:")
    printSolution(matrix, num_rows, num_cols, variables, variable_values)