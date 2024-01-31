import itertools
import sys

#counter =0
#true_clauses = []

def parse_dimacs_path(path):
    cnf = []
    num_vars = 0
    num_clauses = 0
    try:
        with open(path, 'r') as file:
            for line in file:
                tokens = line.split()

                # Skip comments
                if len(tokens) > 0 and tokens[0] == 'c':
                    continue

                # Read the number of variables and clauses
                elif len(tokens) > 1 and tokens[0] == 'p' and tokens[1] == 'cnf':
                    num_vars = int(tokens[2])
                    num_clauses = int(tokens[3])

                # Read the clauses
                elif len(tokens) > 0:
                    clause = [int(literal) for literal in tokens[:-1]]  # Discard the '0' at the end
                    cnf.append(clause)

    except FileNotFoundError:
        print(f"File not found: {path}")
        return [], 0, 0

    return cnf, num_vars, num_clauses

def decide_assignment(assignments, unassigned_vars, guesses):
    # Select the next unassigned variable and assign it to true.
    var = unassigned_vars.pop()
    assignments.append(var)
    guesses.add(var)  # Add the variable to the guesses set.
    return assignments, unassigned_vars, guesses


def backtrack_assignment(assignments, unassigned_vars, guesses):
    # Remove the last decision variable assignment/
    for literal in guesses:
        is_last_guess = True
        index = assignments.index(literal)
        for i in range(index + 1, len(assignments) - 1):
            if assignments[i] in guesses:
                is_last_guess = False  # There is a newer guess.
                break

        if is_last_guess:  # No newer guess.
            # Remove the last guess and the assignments after it from the assignments list.
            unassigned_vars.extend(abs(var) for var in assignments[index + 1:])
            assignments = assignments[0:index]

            # Change the guess for the last guess and remove it from the guesses set..
            assignments.append(-1 * literal)
            guesses.remove(literal)
            return assignments, unassigned_vars, guesses


def unit_propagate(clauses, assignments, unassigned_vars, num_vars):
    unsatisfied_clauses = clauses.copy()

    # Remove all satisfied clauses.
    for literal in assignments:
        for clause in unsatisfied_clauses:
            if literal in clause:
                unsatisfied_clauses.remove(clause)
    while True:
        unit_clause = None
        for clause in unsatisfied_clauses:
            unassigned_count = 0  # Counts unassigned variables in the clause.
            unassigned_var = None
            for literal in clause:
                var = abs(literal)
                if literal not in assignments and -1 * literal not in assignments:  # variable is not assigned.
                    unassigned_count += 1
                    unassigned_var = var
            if unassigned_count == 0:
                # All literals in the clause are assigned, and the clause is not satisfied. Stop propagate.
                return False, assignments
            elif unassigned_count == 1:
                # Unit clause found, assign the unassigned literal.
                unit_clause = (clause, unassigned_var)
                break

        if unit_clause is None:
            # No unit clause found, exit the loop - Can't propagate anymore.
            break

        # Assign the literal in the unit clause
        clause, var = unit_clause
        literal = next(lit for lit in clause if abs(lit) == var)
        assignments.append(literal)
        unassigned_vars.remove(var)
        # Remove satisfied clauses
        unsatisfied_clauses = [c for c in unsatisfied_clauses if literal not in c]
    #print(clauses)
    #print(counter)
    #true_clauses = clauses
    if len(assignments) == num_vars:
        print("sat")
        list_of_vars=[]
        duplicate_vars=[]
        for c in clauses:
            for v in c:
                list_of_vars.append(v)
        list_of_vars=sorted(list_of_vars, key=abs)
        for v in list_of_vars:
            if abs(v) in duplicate_vars:
                continue
            else:
                duplicate_vars.append(v)
                if v<0:
                    v=abs(v)
                    print(f"{v}: false ", end="\n")
                else:
                    print(f"{v}: true ", end="\n")
    return True, assignments


def dpll_solve(cnf, num_vars, num_clauses):
    assignments = []

    unassigned_vars = list(range(1, num_vars + 1))
    guesses = set()  # Set of guesses.
    while True:
        if unit_propagate(cnf, assignments, unassigned_vars,num_vars)[0]:  # Try to propogate.
            if len(assignments) == num_vars:
                # All variables are assigned, and and clauses are satisfied. The assignment satisfies the formula.
                return True
            else:
                # No clause is unsatisfied, but not all variables are assigned. Make a decision on the next variable
                # assignment.
                assignments, unassigned_vars, guesses = decide_assignment(assignments, unassigned_vars, guesses)
        else:
            if len(guesses) == 0:
                # Not all clauses are satisfied, but no assignment is a guess. The formula is unsatisfiable.
                return False
            else:
                # Not all clauses are satisfied, but there is an assignment which is a guess. Backtrack to the
                # previous decision level.
                assignments, unassigned_vars, guesses = backtrack_assignment(assignments, unassigned_vars, guesses)


def naive_solve(cnf, num_vars, num_clauses):
    optional_assignment = itertools.product([False, True], repeat=num_vars)  # All possible assignments.
    for assignment in optional_assignment:
        is_ass_true = True  # Formula is satisfable if all clauses are satisfied.
        for clause in cnf:
            is_clause_true = False
            for literal in clause:
                var = abs(literal)
                if literal > 0:  # If positive literal.
                    value = assignment[var - 1]
                else:
                    value = not assignment[var - 1]
                if value:  # If literal assigned to True.
                    is_clause_true = True  # The clause is satisfied if at least one of its literals assigned to True.
                    break
            if not is_clause_true:  # If one clause is not satisfied, then formula is unsatisfiable.
                is_ass_true = False
                break
        if is_ass_true:
            print("sat")
            for idx, value in enumerate(assignment, start=1):
                if value is True:
                    print(f"{idx}: true", end="\n")
                else:
                    print(f"{idx}: false", end="\n")
            return True
    return False


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python your_script.py <path_to_cnf_file> <algorithm>")
        sys.exit(1)

        # get path to cnf file from the command line
    path = sys.argv[1]

    # Get algorithm from the command line
    algorithm = sys.argv[2]

    # make sure that algorithm is either "naive" or "dpll"
    assert (algorithm in ["naive", "dpll"])

    # parse the file
    cnf, num_vars, num_clauses = parse_dimacs_path(path)

    # check satisfiability based on the chosen algorithm
    # and print the result
    if algorithm == "naive":
        answer = naive_solve(cnf, num_vars, num_clauses)
        if answer is True:
            pass
        else:
            print("unsat")

    else:
        answer = dpll_solve(cnf, num_vars, num_clauses)
        if answer is True:
            pass
        else:
            print("unsat")
