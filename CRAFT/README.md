# CRAFT-Algorithm
Implementation of the CRAFT (Computerized Relative Allocation of Facilities Technique) algorithm for facility layout optimization, with flow-based cost calculation, layout improvement via swaps, and example data for experimentation.

# CRAFT Facility Layout Optimizer

This repository contains a Python implementation of **CRAFT**
(**C**omputerized **R**elative **A**llocation of **F**acilities **T**echnique),
a heuristic for improving facility layouts based on flow and distance between departments.

The script is an **interactive command-line tool** that:

- Accepts department locations (as rectangles or as a distance matrix).
- Accepts inter-department flows and handling costs.
- Builds a distance matrix (Manhattan or Euclidean).
- Uses a CRAFT-style **pairwise swap local search** to reduce total material handling cost.
- Prints the improved layout, cost savings, and (optionally) the full improvement history.

---

## Table of Contents

- [CRAFT Facility Layout Optimizer](#craft-facility-layout-optimizer)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Usage](#usage)
    - [1. Distance Input Options](#1-distance-input-options)
      - [Option 1: From Department Rectangles](#option-1-from-department-rectangles)
      - [Option 2: Direct Distance Matrix Input](#option-2-direct-distance-matrix-input)
    - [2. Flow Matrix (F)](#2-flow-matrix-f)
    - [3. Handling-Cost Matrix (C)](#3-handling-cost-matrix-c)
    - [4. Verbose Swap Logs](#4-verbose-swap-logs)
    - [5. Fixed Departments](#5-fixed-departments)
    - [Output Interpretation](#output-interpretation)
    - [Optional Cost History](#optional-cost-history)
  - [Algorithm Details](#algorithm-details)
    - [Cost Function](#cost-function)
    - [Local Search](#local-search)
  - [Project Structure](#project-structure)
  - [Extending and Reusing the Code](#extending-and-reusing-the-code)
  - [Limitations and Notes](#limitations-and-notes)
  - [Contributing](#contributing)
  - [License](#license)

---

## Features

- **Interactive CLI** – No command-line arguments required; prompts guide you through all inputs.
- **Flexible distance acquisition:**

  - Generate distances from **department rectangles** using their geometric centers.
  - Or directly provide a **distance matrix**.

- **Two distance metrics:**

  - **Manhattan (L1)**
  - **Euclidean (L2)**

- **Asymmetric flow allowed** – Flow from i→j can differ from j→i.
- **Custom handling costs** – Per-pair per-unit-flow per-unit-distance costs via matrix `C`, or use a simple all-ones matrix.
- **CRAFT-style local search:**

  - Greedy pairwise swaps to iteratively reduce cost.
  - Optionally **fix** certain departments so they never move.

- **Detailed reporting:**

  - Original cost vs. improved cost.
  - Cost savings.
  - Final assignment in both “Department → Location” and “Location order” views.
  - Optional cost history of all improving swaps.

---

## Requirements

- **Python:** 3.6+ (f-strings are used; 3.8+ recommended)
- **Libraries:** only standard library modules:

  - `math`
  - `itertools`

No external third-party packages are required.

---

## Installation

1. Clone or download this repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. The main script is:

   ```text
   CRAFT (Final).py
   ```

   > 💡 For convenience, you may want to rename it to `craft.py`, but the code works as-is.

3. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Unix/macOS
   # or
   .venv\Scripts\activate      # on Windows
   ```

---

## Quick Start

From the repository folder:

```bash
# Unix/macOS (quote the filename because of spaces and parentheses)
python "CRAFT (Final).py"

# or, if you renamed it:
python craft.py
```

You will be prompted step-by-step to:

1. Choose how to provide distances (rectangles or matrix).
2. Enter the flow matrix.
3. Enter or choose handling costs.
4. Decide whether to see verbose swap logs.
5. Optionally fix some departments.
6. View the improved layout and cost savings.

---

## Usage

When you run the script, it starts an interactive session:

```text
=== CRAFT (Computerized Relative Allocation of Facilities Technique) ===

Choose an option for DISTANCES:
1) Generate from department rectangles (centers) → choose metric
2) Enter a distance matrix (compact rows; diagonal auto-zero)
Enter 1 or 2:
```

### 1. Distance Input Options

You must first define the **distance matrix** between departments. There are two options.

#### Option 1: From Department Rectangles

Choose option **1**:

```text
Enter 1 or 2: 1
Enter the number of departments (at least 2):
```

- Let `a` = number of departments (A, B, C, ...).
- Departments are automatically labeled as **A, B, C, ...** based on their index.

You then choose how to enter the rectangles:

```text
How would you like to enter rectangles?
1) One line per department:  x_start,x_end,y_start,y_end
2) Paste ALL departments at once (semicolon or newline separated)
Enter 1 or 2:
```

Each rectangle line must be in the form:

```text
x_start,x_end,y_start,y_end
```

For example, for three departments:

```text
Dept A (x_start,x_end,y_start,y_end): 0,40,0,20
Dept B (x_start,x_end,y_start,y_end): 40,80,0,20
Dept C (x_start,x_end,y_start,y_end): 0,40,20,40
```

- If bounds are given in reverse (e.g., `40,0`), they are automatically normalized so that `x_start <= x_end` and `y_start <= y_end`.
- The script computes the **center** of each rectangle and then builds a pairwise distance matrix from those centers.

Next, you choose the distance metric:

```text
Choose distance metric:
1) Manhattan (L1)
2) Euclidean (L2)
Enter 1 or 2:
```

The script then builds a symmetric distance matrix and ensures zero diagonal (distance from a department to itself is 0).

#### Option 2: Direct Distance Matrix Input

Choose option **2**:

```text
Enter 1 or 2: 2
Enter the number of departments (at least 2):
```

You will then enter the distance matrix in **compact row format**.

- Departments are labeled **A, B, C, ...**.
- For each department row, you input **n−1 values**, corresponding to all other departments in **label order**, excluding itself.
- The diagonal entries are automatically set to 0.

Example for 3 departments (A, B, C):

- Row for A: distances to B, C
- Row for B: distances to A, C
- Row for C: distances to A, B

The script prompts like:

```text
Enter the DISTANCE matrix in compact rows (diagonal is auto-zero).

Distance row for A → [B, C] (comma-separated):
Distance row for B → [A, C] (comma-separated):
Distance row for C → [A, B] (comma-separated):
```

After entering the matrix, you have the option to **force-symmetrize**:

```text
Force-symmetrize the distance matrix and zero the diagonal? [y/n]:
```

If you answer **y**, the matrix is replaced with:

```text
D_sym[i][j] = D_sym[j][i] = 0.5 * (D[i][j] + D[j][i])
D_sym[i][i] = 0.0
```

This is useful if the raw entries are slightly inconsistent.

---

### 2. Flow Matrix (F)

After the distance matrix is established:

```text
Enter the FLOW matrix (compact rows, diagonal auto-zero). (Asymmetric flows allowed.)
Flow row for A → [B, C] (comma-separated):
Flow row for B → [A, C] (comma-separated):
Flow row for C → [A, B] (comma-separated):
```

- Flow represents the amount of “traffic” or material moved between departments.
- As with the distance matrix, you enter **n−1** values per row, in label order excluding the row label.
- Flows can be **asymmetric**: `F[i][j]` does not have to equal `F[j][i]`.

---

### 3. Handling-Cost Matrix (C)

Handling cost per unit flow per unit distance between departments:

```text
Handling-cost (per unit flow per unit distance) matrix C[i][j]:
1) I will enter it (compact rows, diagonal auto-zero)
2) Use all-ones (no per-pair weighting)
Enter 1 or 2:
```

- If you choose **1**, you again enter a compact-row matrix similar to distances and flows.
- If you choose **2**, the script uses a matrix of all ones (except zero on the diagonal), i.e. no special weighting: the cost is driven purely by flow × distance.

---

### 4. Verbose Swap Logs

You can choose whether to print details about each improving swap:

```text
Do you want verbose swap logs?
1) Yes
2) No
Enter 1 or 2:
```

If **Yes**, each accepted swap during the local search prints:

```text
Swap A ↔ C | Δ=-123.4570 | Cost=790.0000
```

Where:

- `Δ` is the change in total cost (negative means improvement).
- `Cost` is the new total cost after the swap.

---

### 5. Fixed Departments

You may designate certain departments as **fixed** so they never move from their initial locations:

```text
Enter fixed departments (comma-separated labels) or leave empty:
```

Examples:

- `A`
- `A, C`
- Leave empty for no fixed departments.

Unknown labels are ignored with a warning.

---

### Output Interpretation

After all inputs are provided, the script:

1. Computes the **original total cost** for the identity assignment (department i at location i).
2. Prints the **distance matrix** with labels.
3. Runs the CRAFT local search to find a lower-cost assignment.
4. Prints:

```text
Distance Matrix:
    A       B       C
A   0.0000  10.0000 20.0000
B   10.0000 0.0000  15.0000
C   20.0000 15.0000 0.0000

Original Total Cost (identity assignment): 12345.6790

Minimum Total Cost: 9876.5430
Cost Savings vs original: 2470.1360

Final assignment (Department → Location index):
  A → 2
  B → 1
  C → 3

Departments in location order (1..n):
  B  A  C
```

Interpretation:

- **Original Total Cost** – cost before any swaps (baseline layout).
- **Minimum Total Cost** – cost after optimization.
- **Cost Savings** – difference between original and minimum cost.
- **Department → Location index** – mapping of each department label to its location index (1-based).
- **Departments in location order** – which department ends up at location 1, 2, 3, etc.

---

### Optional Cost History

At the end, you can choose to print the entire cost history:

```text
Print cost history? [y/n]:
```

If **Yes**, you will see something like:

```text
Cost history:
  Initial                  12345.67890
  Swap A ↔ C              11000.12340
  Swap B ↔ C              9876.54320
```

This shows each improving move and the corresponding cost.

---

## Algorithm Details

The code implements a **CRAFT-style local search** on a quadratic assignment cost:

### Cost Function

Given:

- `F[i][j]` – flow from department `i` to department `j`
- `D[p][q]` – distance between locations `p` and `q`
- `C[i][j]` – handling cost per unit flow per unit distance for pair `(i, j)`
- `perm[i]` – location index assigned to department `i`

The total cost is:

[
\text{Cost} = \sum\_{i \ne j} F[i][j] \cdot D[\text{perm}[i]][\text{perm}[j]] \cdot C[i][j]
]

### Local Search

- Start with the **identity assignment**: department `i` is at location `i`.
- Consider swapping pairs of departments `(i, j)` (except those in the fixed set).
- For each pair, compute the **change in cost** using an efficient `O(n)` incremental formula (`delta_swap`) rather than recomputing the full cost.
- Choose the **best improving swap** in each pass:

  - If the best delta is negative (improvement), perform that swap.
  - Record the new cost.
  - Repeat until **no improving swap** remains (local optimum).

- The search stops when:

  - No improving pair is found, or
  - The maximum passes limit (`max_passes`, default 10,000) is reached.

---

## Project Structure

Current repository structure (simplified):

```text
.
├── CRAFT (Final).py   # Main and only script with all logic & interactive CLI
└── README.md          # This documentation
```

All functionality (data input, distance computation, cost computation, local search, and CLI) is contained in `CRAFT (Final).py`.

---

## Extending and Reusing the Code

You can also reuse the core functions programmatically by importing the script in another Python file (after renaming if desired):

```python
from craft import (
    compute_cost,
    craft_local_search,
    manhattan_distance_matrix,
    euclidean_distance_matrix,
    symmetrize_with_zero_diag,
)
```

Example programmatic use:

```python
from craft import compute_cost, craft_local_search, manhattan_distance_matrix, symmetrize_with_zero_diag

# Example: 3 departments with simple coordinates
points = [[0, 0], [10, 0], [0, 10]]
D = manhattan_distance_matrix(points)
D = symmetrize_with_zero_diag(D)

F = [
    [0, 5, 2],
    [4, 0, 3],
    [1, 2, 0],
]

# All-ones handling cost
C = [
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0],
]

department_labels = ["A", "B", "C"]
initial_perm = [0, 1, 2]

best_perm, best_cost, history = craft_local_search(F, D, C, department_labels, initial_perm=initial_perm)
print("Best permutation:", best_perm)
print("Best cost:", best_cost)
```

This can be a starting point for integrating CRAFT-like optimization into a larger system or GUI.

---

## Limitations and Notes

- **Number of departments & labels**

  - Departments are labeled sequentially starting from `'A'` using ASCII arithmetic.
  - For a large number of departments, labels will continue into non-alphabet characters (after `'Z'`). In practice, keeping department count ≤ 26 is recommended if you want clean letter labels.

- **Local optimum only**

  - The algorithm is purely greedy and finds a **local** optimum, not guaranteed global optimum.
  - Different initial layouts or additional metaheuristics (e.g., random restarts) are not implemented but could be added.

- **Interactive only**

  - The script is currently fully interactive and does not support command-line arguments for batch runs.
  - For automation, you can either:

    - Wrap the core functions programmatically, or
    - Modify `main()` to accept parameters instead of using `input()`.

- **No persistence**

  - The script does not save or load configurations from files by default.

---

## Contributing

Contributions are welcome! Possible improvements include:

- Adding command-line arguments to support non-interactive usage.
- Implementing alternative initial layouts (e.g., random permutations).
- Adding metaheuristics (e.g., simulated annealing, tabu search) to escape local minima.
- Improved validation and richer error messages for user inputs.
- Support for loading/saving layouts and matrices from/to CSV or JSON.

If you’d like to contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-improvement`).
3. Commit your changes (`git commit -am "Add my improvement"`).
4. Push the branch (`git push origin feature/my-improvement`).
5. Open a Pull Request describing your changes.

---

## License

A specific license is **not yet defined** in the code or repository.

- If you are the repository owner, consider adding a license file (e.g., `MIT`, `Apache-2.0`, or `GPL-3.0`) and updating this section accordingly.
- Until a license is explicitly specified, third-party usage rights remain unclear; please treat the code as “all rights reserved” by default.

