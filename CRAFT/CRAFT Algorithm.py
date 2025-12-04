from itertools import combinations
import math

def ask_int(prompt, cond=None, err_msg="Invalid input."):
    while True:
        try:
            val = int(input(prompt).strip())
            if cond and not cond(val):
                print(err_msg)
                continue
            return val
        except ValueError:
            print("Please enter an integer.")

def ask_float(prompt):
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Please enter a number.")

def ask_yes_no(prompt):
    while True:
        s = input(prompt + " [y/n]: ").strip().lower()
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("Please answer y or n.")

def print_matrix_with_labels(title, labels, M):
    print(f"\n{title}")
    header = [" "] + labels
    print("\t".join(header))
    for lab, row in zip(labels, M):
        row_str = [lab] + [f"{v:.4f}" if isinstance(v, float) else str(v) for v in row]
        print("\t".join(row_str))

def zero_matrix(n):
    return [[0.0]*n for _ in range(n)]

def ones_matrix(n):
    return [[1.0]*n for _ in range(n)]

def copy_matrix(M):
    return [row.copy() for row in M]

def ask_matrix_compact(labels, name="Matrix"):
    """
    For each row i, asks for n-1 comma-separated numbers for j != i.
    Target order per row is all labels excluding the row label, in label order.
    Diagonal is auto-zero.
    """
    n = len(labels)
    M = zero_matrix(n)
    for i, src in enumerate(labels):
        targets = [lab for k, lab in enumerate(labels) if k != i]
        targets_str = ", ".join(targets)
        while True:
            line = input(f"{name} row for {src} → [{targets_str}] (comma-separated): ").strip()
            try:
                vals = [float(x.strip()) for x in line.split(",") if x.strip() != ""]
                if len(vals) != n - 1:
                    print(f"Please enter exactly {n-1} values.")
                    continue
                t_idx = 0
                for j in range(n):
                    if j == i:
                        M[i][j] = 0.0
                    else:
                        M[i][j] = vals[t_idx]
                        t_idx += 1
                break
            except ValueError:
                print("All entries must be numbers. Try again.")
    return M

# =========================
# Rectangles & distances
# =========================

def parse_one_rectangle(line):
    # Expect: "x_start,x_end,y_start,y_end"
    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 4:
        raise ValueError("Enter exactly 4 comma-separated values: x_start,x_end,y_start,y_end")
    x0, x1, y0, y1 = map(float, parts)
    # normalize if user gave reversed bounds
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return [x0, x1, y0, y1]

def parse_rectangles_bulk(block, expected_count=None):
    raw = block.strip()
    if ";" in raw:
        entries = [e.strip() for e in raw.split(";") if e.strip()]
    else:
        entries = [e.strip() for e in raw.splitlines() if e.strip()]
    rects = [parse_one_rectangle(e) for e in entries]
    if expected_count is not None and len(rects) != expected_count:
        raise ValueError(f"Expected {expected_count} departments, got {len(rects)}.")
    return rects

def central_points_from_rects(departments):
    cps = []
    for x0, x1, y0, y1 in departments:
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        cps.append([cx, cy])
    return cps

def manhattan_distance_matrix(points):
    n = len(points)
    D = zero_matrix(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                D[i][j] = abs(points[i][0]-points[j][0]) + abs(points[i][1]-points[j][1])
    return D

def euclidean_distance_matrix(points):
    n = len(points)
    D = zero_matrix(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = points[i][0]-points[j][0]
                dy = points[i][1]-points[j][1]
                D[i][j] = math.hypot(dx, dy)
    return D

def symmetrize_with_zero_diag(M):
    n = len(M)
    S = zero_matrix(n)
    for i in range(n):
        for j in range(n):
            if i == j:
                S[i][j] = 0.0
            else:
                S[i][j] = 0.5 * (M[i][j] + M[j][i])
    return S

# =========================
# CRAFT core
# =========================

def compute_cost(F, D, C, perm):
    """Cost = sum_{i!=j} F[i][j] * D[perm[i]][perm[j]] * C[i][j]."""
    n = len(F)
    total = 0.0
    for i in range(n):
        pi = perm[i]
        for j in range(n):
            if i == j:
                continue
            pj = perm[j]
            total += F[i][j] * D[pi][pj] * C[i][j]
    return total

def delta_swap(i, j, F, D, C, perm):
    """
    O(n) cost change when swapping departments i and j.
    Only pairs touching i or j contribute to the delta.
    """
    if i == j:
        return 0.0
    n = len(F)
    pi, pj = perm[i], perm[j]
    dlt = 0.0

    for k in range(n):
        if k == i or k == j:
            continue
        pk = perm[k]
        # i with k
        dlt += F[i][k] * (D[pj][pk] - D[pi][pk]) * C[i][k]
        dlt += F[k][i] * (D[pk][pj] - D[pk][pi]) * C[k][i]
        # j with k
        dlt += F[j][k] * (D[pi][pk] - D[pj][pk]) * C[j][k]
        dlt += F[k][j] * (D[pk][pi] - D[pk][pj]) * C[k][j]

    # i with j
    dlt += F[i][j] * (D[pj][pi] - D[pi][pj]) * C[i][j]
    dlt += F[j][i] * (D[pi][pj] - D[pj][pi]) * C[j][i]
    return dlt

def craft_local_search(F, D, C, department_labels, initial_perm=None, verbose=False, fixed_indices=None, max_passes=10_000):
    """
    Greedy pairwise-swap descent until no improving swap remains.
    fixed_indices: set of department indices that must not move.
    Returns (best_perm, best_cost, history)
    """
    n = len(F)
    perm = list(range(n)) if initial_perm is None else initial_perm[:]
    fixed = set(fixed_indices or [])
    best_cost = compute_cost(F, D, C, perm)
    history = [("Initial", best_cost)]

    passes = 0
    while passes < max_passes:
        passes += 1
        improved = False
        best_delta = 0.0
        best_pair = None

        for i in range(n - 1):
            if i in fixed: 
                continue
            for j in range(i + 1, n):
                if j in fixed:
                    continue
                d = delta_swap(i, j, F, D, C, perm)
                if d < best_delta:  # strictly improving
                    best_delta = d
                    best_pair = (i, j)

        if best_pair is None:
            break  # local optimum reached

        # apply best swap
        i, j = best_pair
        perm[i], perm[j] = perm[j], perm[i]
        best_cost += best_delta
        label_i, label_j = department_labels[i], department_labels[j]
        history.append((f"Swap {label_i} ↔ {label_j}", best_cost))
        improved = True
        if verbose:
            print(f"Swap {label_i} ↔ {label_j} | Δ={best_delta:.4f} | Cost={best_cost:.4f}")

        if not improved:
            break

    return perm, best_cost, history

# =========================
# Program entry (interactive)
# =========================

def main():
    print("=== CRAFT (Computerized Relative Allocation of Facilities Technique) ===")

    # ---------- Distance acquisition ----------
    print("\nChoose an option for DISTANCES:")
    print("1) Generate from department rectangles (centers) → choose metric")
    print("2) Enter a distance matrix (compact rows; diagonal auto-zero)")
    option = ask_int("Enter 1 or 2: ", cond=lambda x: x in (1, 2), err_msg="Please enter 1 or 2.")

    if option == 1:
        a = ask_int("Enter the number of departments (at least 2): ", cond=lambda x: x >= 2, err_msg="Must be at least 2.")
        department_labels = [chr(ord('A') + i) for i in range(a)]

        print("\nHow would you like to enter rectangles?")
        print("1) One line per department:  x_start,x_end,y_start,y_end")
        print("2) Paste ALL departments at once (semicolon or newline separated)")
        mode_rect = ask_int("Enter 1 or 2: ", cond=lambda x: x in (1,2), err_msg="Please enter 1 or 2.")

        departments = []
        if mode_rect == 1:
            for i in range(a):
                while True:
                    try:
                        line = input(f"Dept {department_labels[i]} (x_start,x_end,y_start,y_end): ").strip()
                        departments.append(parse_one_rectangle(line))
                        break
                    except ValueError as e:
                        print(e)
        else:
            while True:
                print(f"\nPaste {a} departments (e.g., 0,40,0,20; 10,20,5,25; ...)")
                block = input(">>> ")
                try:
                    departments = parse_rectangles_bulk(block, expected_count=a)
                    break
                except ValueError as e:
                    print(e)

        cps = central_points_from_rects(departments)

        print("\nChoose distance metric:")
        print("1) Manhattan (L1)")
        print("2) Euclidean (L2)")
        metric = ask_int("Enter 1 or 2: ", cond=lambda x: x in (1,2), err_msg="Please enter 1 or 2.")
        if metric == 1:
            distance_matrix = manhattan_distance_matrix(cps)
        else:
            distance_matrix = euclidean_distance_matrix(cps)

        # Symmetrize for safety (centers produce symmetric anyway)
        distance_matrix = symmetrize_with_zero_diag(distance_matrix)

    else:
        a = ask_int("Enter the number of departments (at least 2): ",
                    cond=lambda x: x >= 2, err_msg="Must be at least 2.")
        department_labels = [chr(ord('A') + i) for i in range(a)]
        print("\nEnter the DISTANCE matrix in compact rows (diagonal is auto-zero).")
        distance_matrix = ask_matrix_compact(department_labels, name="Distance")

        if ask_yes_no("Force-symmetrize the distance matrix and zero the diagonal?"):
            distance_matrix = symmetrize_with_zero_diag(distance_matrix)

    # ---------- Flow matrix (F) ----------
    print("\nEnter the FLOW matrix (compact rows, diagonal auto-zero). (Asymmetric flows allowed.)")
    flow_matrix = ask_matrix_compact(department_labels, name="Flow")

    # ---------- Handling cost matrix (C) ----------
    print("\nHandling-cost (per unit flow per unit distance) matrix C[i][j]:")
    print("1) I will enter it (compact rows, diagonal auto-zero)")
    print("2) Use all-ones (no per-pair weighting)")
    handling_option = ask_int("Enter 1 or 2: ", cond=lambda x: x in (1,2))
    if handling_option == 1:
        handling_cost = ask_matrix_compact(department_labels, name="Handling cost")
    else:
        handling_cost = ones_matrix(a)

    # ---------- Verbose & fixed departments ----------
    print("\nDo you want verbose swap logs?")
    print("1) Yes")
    print("2) No")
    verbose = (ask_int("Enter 1 or 2: ", cond=lambda x: x in (1,2)) == 1)

    fixed_input = input("\nEnter fixed departments (comma-separated labels) or leave empty: ").strip()
    fixed_indices = set()
    if fixed_input:
        for tok in fixed_input.split(","):
            lab = tok.strip()
            if lab in department_labels:
                fixed_indices.add(department_labels.index(lab))
            else:
                print(f"Warning: unknown label '{lab}' ignored.")

    # ---------- Initial cost ----------
    n = a
    initial_perm = list(range(n))  # dept i at location i
    original_cost = compute_cost(flow_matrix, distance_matrix, handling_cost, initial_perm)
    print_matrix_with_labels("Distance Matrix:", department_labels, distance_matrix)
    print(f"\nOriginal Total Cost (identity assignment): {original_cost:.4f}")

    # ---------- Run CRAFT local search ----------
    best_perm, best_cost, history = craft_local_search(
        flow_matrix, distance_matrix, handling_cost,
        department_labels=department_labels,
        initial_perm=initial_perm,
        verbose=verbose,
        fixed_indices=fixed_indices
    )

    # ---------- Report ----------
    savings = original_cost - best_cost
    print(f"\nMinimum Total Cost: {best_cost:.4f}")
    print(f"Cost Savings vs original: {savings:.4f}")

    print("\nFinal assignment (Department → Location index):")
    for i, lab in enumerate(department_labels):
        print(f"  {lab} → {best_perm[i]+1}")

    # Also show by location order (who sits at each location k?)
    inverse = [None]*n
    for dept, loc in enumerate(best_perm):
        inverse[loc] = department_labels[dept]
    print("\nDepartments in location order (1..n):")
    print("  " + "  ".join(inverse))

    # Optional: show brief history
    if ask_yes_no("\nPrint cost history?"):
        print("\nCost history:")
        for step, cost in history:
            print(f"  {step:<24}  {cost:.4f}")

if __name__ == "__main__":
    main()
