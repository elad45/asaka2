# importing system module for reading files
import sys
import itertools


# in what follows, a *formula* is a collection of clauses,
# a clause is a collection of literals,
# and a literal is a non-zero integer.

# input path:  a path to a cnf file
# output: the formula represented by the file, 
#         the number of variables, 
#         and the number of clauses
def parse_dimacs_path(path):
    cnf = []
    try:
        with open(path, 'r') as f:
            lines = f.readlines()

            # Parse header line
            header = lines[0].strip().split()
            n_vars = int(header[2])
            m_clauses = int(header[3])

            # Parse clauses
            for line in lines[1:]:
                clause = [int(x) for x in line.strip().split()[:-1]]
                cnf.append(clause)

            # print(f"{n_vars} {m_clauses} {cnf}")
    except:
        print("invalid path")
        sys.exit(1)
    return cnf, n_vars, m_clauses


def clause_satisfication(clause, assignment):
    for literal in clause:
        if literal > 0:
            if assignment[literal - 1] == True:
                return True
        else:
            if assignment[-literal - 1] == False:
                return True
    return False

def print_assignment_dpll(assignment):
    print("sat")
    for idx,value in enumerate(assignment,start=1):
        if value>0:
            print(f"{idx}: true",end="\n")
        else:
            print(f"{idx}: false",end="\n")
def print_assignment(assignment):
    print("sat")
    for idx, value in enumerate(assignment, start=1):
        if value is True:
            print(f"{idx}: true", end="\n")
        else:
            print(f"{idx}: false", end="\n")

def naive_solve(cnf, n_vars, n_clauses):
    # Generate all possible truth value assignments for the variables
    all_assignments = itertools.product([False, True], repeat=n_vars)
    for assignment in all_assignments:
        if all(clause_satisfication(clause, assignment) for clause in cnf):
            print_assignment(assignment)
            break
    else:
        print("unsat")


def get_unsatisfied_clauses(cnf, assigned):
    unsatisfied_clauses = cnf.copy()
    for literal in assigned:
        for clause in unsatisfied_clauses:
            if literal in clause:
                unsatisfied_clauses.remove(clause)
    return unsatisfied_clauses


def backtrack(assigned, unassigned, d):
    # get the index of the last "decide" literal
    guess_index = assigned.index(d[-1])
    # place all the literals after the guess back to unassigned list
    for i in range(guess_index + 1, len(assigned)):
        unassigned.append(abs(assigned[i]))
    # remove guess and all literals after guess from assigned list
    assigned = assigned[:guess_index]
    # change guess to its complement and append to assigned list
    assigned.append(-d[-1])
    # remove guess from d
    d.pop()
    return assigned, unassigned, d


def decide(assigned, unassigned, d):
    if len(unassigned) == 0:
        return True, assigned, unassigned
    literal = unassigned.pop()
    assigned.append(literal)
    d.append(literal)
    return assigned, unassigned, d


def unit_propogate(cnf, assigned, unassigned):
    unsatisfied_clauses = get_unsatisfied_clauses(cnf, assigned)
    while True:
        if len(unsatisfied_clauses) == 0:
            return True, assigned, unassigned
        chosen_clause = None
        for clause in unsatisfied_clauses:
            count_unassigned_literals = 0
            unassigned_literal = None

            for literal in clause:
                var = abs(literal)
                if var in unassigned:
                    count_unassigned_literals += 1
                    unassigned_literal = literal
            # the clause is unsatisfiable because all literals are assigned and the result is false
            if count_unassigned_literals == 0:
                return False, assigned, unassigned
            # one literal is not assigned so it must be evaluated True
            if count_unassigned_literals == 1:
                chosen_clause = [clause, unassigned_literal]
                break

        if chosen_clause is None:
            return True, assigned, unassigned
        else:
            literal = chosen_clause[1]
            unassigned.remove(abs(literal))
            assigned.append(literal)
            unsatisfied_clauses = [clause for clause in unsatisfied_clauses if literal not in clause]

# input cnf: a formula
# input n_vars: the number of variables in the formula
# input n_clauses: the number of clauses in the formula
# output: True if cnf is satisfiable, False otherwise
def dpll_solve(cnf, n_vars, n_clauses):
    assigned = []
    unassigned = list(range(1, n_vars + 1))
    d = []

    while True:
        #first trying to poropogate
        is_propogated, assigned, unassigned = unit_propogate(cnf, assigned, unassigned)
        if is_propogated:
            if len(assigned) == n_vars:
                print_assignment_dpll(assigned)
                return
                #return True,assigned
            # propagate success, now trying to guess (decide)
            assigned, unassigned, d = decide(assigned, unassigned, d)
            # now trying to backtrack
        else:
            if len(d) == 0:
                print("unsat")
                return
            else:
                assigned, unassigned, d = backtrack(assigned, unassigned, d)
######################################################################

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("expecting 2 arguments")
        sys.exit(1)
    # get path to cnf file from the command line
    path = sys.argv[1]

    # get algorithm from the command line
    algorithm = sys.argv[2]

    # make sure that algorithm is either "naive" or "dpll"
    assert (algorithm in ["naive", "dpll"])

    # parse the file
    cnf, num_vars, num_clauses = parse_dimacs_path(path)

    # check satisfiability based on the chosen algorithm
    # and print the result
    if algorithm == "naive":
        naive_solve(cnf, num_vars, num_clauses)
    else:
        dpll_solve(cnf, num_vars, num_clauses)
