# Computational Algorithms for Facilities Planning

[![CI](https://github.com/sina-04/Computational-Algorithms-for-Facilities-Planning/actions/workflows/ci.yml/badge.svg)](https://github.com/sina-04/Computational-Algorithms-for-Facilities-Planning/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python tools for experimenting with facility-layout planning methods used in
industrial engineering and operations research.

## Current implementation

The repository currently implements **CRAFT** (Computerized Relative
Allocation of Facilities Technique), including:

- Manhattan or Euclidean distance matrices from department rectangles;
- direct distance, flow, and handling-cost matrix input;
- flow-distance cost evaluation;
- greedy pairwise-swap improvement;
- fixed-department constraints and improvement history;
- an interactive command-line interface.

Run it with:

```bash
python craft/craft.py
```

The detailed input guide and model assumptions are documented in
[`craft/README.md`](craft/README.md).

## Roadmap

COFAD, ALDEP, CORELAP, and PLANET are planned extensions; they are not yet
implemented. Each will be added with reproducible examples and tests before it
is listed as available.

## Validation

```bash
python -m unittest discover -s tests -v
```

Tests verify swap-delta calculations and ensure that local search does not
increase the objective value.

## Limitations

The CRAFT implementation uses pairwise-swap descent and may stop at a local
optimum. Its geometric representation uses department centers and does not
enforce every real-world shape, adjacency, aisle, or relocation constraint.

## License

Released under the [MIT License](LICENSE).
