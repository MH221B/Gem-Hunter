import os
from CNF import main as CNF_main
from BruteForce import main as BruteForce_main
from dpll import main as DPLL_main
from walksat import main as WalkSAT_main

def list_text_files(folder_path):
    text_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            text_files.append(file)
    return text_files

if __name__ == '__main__':
    folder_path = 'testcases'
    files = list_text_files(folder_path)
    
    print("Choose an algorithm:")
    print("1. Brute Force")
    print("2. CNF")
    print("3. DPLL")
    print("4. WalkSAT")
    print("0. Exit")
    algorithm = int(input())
    if algorithm == 0:
        exit()
    
    print("Choose an input file:")
    for i, file in enumerate(files):
        print(f"{i + 1}. {file}")
    print("0. Exit")
    file_index = int(input()) - 1
    if file_index == -1:
        exit()
    
    print("Solving...")
    if algorithm == 1:
        BruteForce_main(files[file_index])
    elif algorithm == 2:
        CNF_main(files[file_index])
    elif algorithm == 3:
        DPLL_main(files[file_index])
    elif algorithm == 4:
        WalkSAT_main(files[file_index])