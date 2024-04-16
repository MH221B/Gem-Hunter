

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

def is_valid_solution(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] is None:
                return False
            if isinstance(matrix[i][j], int):
                count_T = sum(1 for x in range(max(0, i-1), min(len(matrix), i+2))
                                for y in range(max(0, j-1), min(len(matrix[0]), j+2))
                                if (x, y) != (i, j) and matrix[x][y] == 'T')
                if count_T != matrix[i][j]:
                    return False
    return True

def solve_gem_hunter(matrix):
    def backtrack(matrix, i, j):
        if i >= len(matrix) or j >= len(matrix[0]):
            return False
        if is_valid_solution(matrix):
            return True
        if matrix[i][j] is None:
            matrix[i][j] = 'T'  # set cell to T
            # recursive call
            if backtrack(matrix, i, j):
                return True
            matrix[i][j] = 'G'  # set cell to G
            # recursive call
            if backtrack(matrix, i, j):
                return True
            matrix[i][j] = None  # reset cell
            return False  # If neither 'T' nor 'G' works, return False
        return backtrack(matrix, i, j+1) if j < len(matrix[0])-1 else backtrack(matrix, i+1, 0)

    return backtrack(matrix, 0, 0)


def print_matrix(matrix):
    for row in matrix:
        print(' '.join(str(cell) if cell is not None else '_' for cell in row))

def main(file_path):
    matrix, _, _ = read_matrix_from_file(file_path)
    print("Problem:")
    print_matrix(matrix)
    solve_gem_hunter(matrix)
    print("\nSolution:")
    print_matrix(matrix)


if __name__ == "__main__":
    main("testcases/11x11.txt")