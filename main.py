import os
from lib import main as LIB_main
from BruteForce import main as BruteForce_main
from dpll import main as DPLL_main
from walksat import main as WalkSAT_main
import time

def list_text_files(folder_path):
    text_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            text_files.append(file)
    return text_files

def save_solution_to_file(solution, file_path, time_taken):
    with open(file_path, 'w') as file:
        for row in solution:
            file.write(' '.join([str(x) for x in row]) + '\n')
        file.write('\n')
        file.write(f"Time taken: {time_taken} seconds")

if __name__ == '__main__':
    folder_path = 'testcases'
    files = list_text_files(folder_path)
    
    while True:
        print("Choose an algorithm:")
        print("1. Brute Force")
        print("2. Library-supported algorithm")
        print("3. DPLL")
        print("4. WalkSAT")
        print("0. Exit")
        algorithm = int(input("Input: "))
        if algorithm == 0:
            exit()
        
        print("Choose an input file:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")
        print("0. Exit")
        file_index = int(input("Input: ")) - 1
        if file_index == -1:
            exit()
        
        print("Solving...")
        if algorithm == 1:
            start = time.time()
            solution = BruteForce_main(files[file_index])
            end = time.time()
            print(f"Time taken for bruteforce algorithm: {end - start} seconds")
            if solution is not None:
                save_solution_to_file(solution, 'solutions/' + files[file_index].replace('.txt', '_BruteForce_solution.txt'), end - start)
        elif algorithm == 2:
            start = time.time()
            solution = LIB_main(files[file_index])
            end = time.time()
            print(f"Time taken for library-supported alogrithm: {end - start} seconds")
            if solution is not None:
                save_solution_to_file(solution, 'solutions/' + files[file_index].replace('.txt', '_LIB_solution.txt'), end - start)
        elif algorithm == 3:
            start = time.time()
            solution = DPLL_main(files[file_index])
            end = time.time()
            print(f"Time taken for DPLL algorithm: {end - start} seconds")
            if solution is not None:
                save_solution_to_file(solution, 'solutions/' + files[file_index].replace('.txt', '_DPLL_solution.txt'), end - start)
        elif algorithm == 4:
            start = time.time()
            solution = WalkSAT_main(files[file_index])
            end = time.time()
            print(f"Time taken for WalkSAT algorithm: {end - start} seconds")
            if solution is not None:
                save_solution_to_file(solution, 'solutions/' + files[file_index].replace('.txt', '_WalkSAT_solution.txt'), end - start)
                
        print("Solution saved to file.")
        print("Press Enter to continue...")
        input()
        os.system('cls' if os.name == 'nt' else 'clear')