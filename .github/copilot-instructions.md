# Copilot Instructions – HSLU TA.DIGITALTWIN: Glucose-Insulin Digital Twin

## Quick Start (Verification)

```bash
# Install dependencies
pip install -r requirements.txt

# Format (auto-fix)
black src/ tests/

# Lint
pylint src/ tests/

# Type check
mypy src/ tests/

# Run tests
pytest
```

All four tools must pass before committing.

---

## Project Overview

**Module:** TA.DIGITALTWIN – Digital Twins and Products  
**Institution:** Hochschule Luzern, Technik & Architektur  
**Goal:** Build a Digital Twin of the human glucose-insulin system using a low-order grey-box compartment model (E-DES-inspired).

### Domain

- **Physical Entity:** Human glucose-insulin system
- **System Input:** Meal glucose equivalent [mmol]
- **System Output:** Interstitial glucose concentration [mmol/L] (CGM measurement)
- **Model Type:** Grey-box ODE compartment model (low-order, physiologically motivated)

### Package Structure

```
src/glucose_insulin/
    __init__.py       – public API exports
    model.py          – ODE compartment model (GlucoseInsulinModel, ModelParameters)
    simulation.py     – simulation runner (run_simulation, SimulationResult)
    utils.py          – unit conversions and helper functions
tests/
    test_model.py     – unit tests (structure, contracts, numerics)
```

### Semester Milestones
| SW | Topic | Status |
| --- | --- | --- |
| SW02 | Model Specification – ODE equations, block diagram | 🔜 |
| SW03 | DT Requirements, System Decomposition, 5D Architecture | 🔜 |
| SW04 | State machine (insulin pump), behaviour models (meal, activity) | 🔜 |
| SW08 | Insulin pump use case, DT-based development | 🔜 |
| SW10 | State estimation (observer), parameter estimation, personalisation | 🔜 |
| SW11 | Data architecture, data flows, interfaces | 🔜 |
| SW12 | Full 5D Digital Twin integration | 🔜 |

---

## Code Style Standards

This project follows the **Google Python Style Guide** strictly.

### Naming

| Element | Convention | Example |
| --- | --- | --- |
| Functions & variables | `snake_case` | `run_simulation`, `meal_rate` |
| Classes | `PascalCase` | `GlucoseInsulinModel` |
| Constants | `UPPER_SNAKE_CASE` | `GLUCOSE_MOLAR_MASS` |
| Private members | `_leading_underscore` | `_absorption_tau` |
| Modules | `snake_case` | `glucose_insulin`, `utils` |

### Imports

Always in this order, separated by blank lines:

```python
# 1. Standard library
import dataclasses
from typing import Optional

# 2. Third-party
import numpy as np
from scipy.integrate import solve_ivp

# 3. Local / project
from glucose_insulin.model import GlucoseInsulinModel
```

Never use wildcard imports (`from module import *`).

### Type Hints

- Required on **all** function signatures (parameters and return types).
- Use `numpy.typing.NDArray[np.float64]` for NumPy arrays.
- Use `from __future__ import annotations` only if needed for forward refs.

```python
# ✅ correct
def meal_glucose_rate(
    time_min: float,
    total_glucose_mmol: float,
    absorption_rate_min: float = 30.0,
) -> float:

# ❌ wrong – missing type hints
def meal_glucose_rate(time_min, total_glucose_mmol, absorption_rate_min=30.0):
```

### Docstrings

Google-format docstrings on **every** public module, class, and function.

```python
def example_function(param: float) -> float:
    """One-line summary ending with a period.

    Longer description if needed. Explain the physics or math
    briefly when relevant to the domain.

    Args:
        param: Description including units in square brackets, e.g. [mmol/L].

    Returns:
        Description including units.

    Raises:
        ValueError: If param is not strictly positive.
    """
```

- Always include **units** in Args/Returns descriptions (e.g. `[mmol/L]`, `[min]`, `[pmol/L]`).
- Private helper functions need at minimum a one-line docstring.

### Line Length & Formatting

- Maximum line length: **79 characters** (Black enforced).
- Black handles all formatting automatically — do not fight it.
- One blank line between methods; two blank lines between top-level definitions.

### Error Handling

- Raise specific exceptions with descriptive messages:
  ```python
  # ✅ correct
  raise ValueError(
      f"absorption_rate_min must be positive, got {absorption_rate_min}"
  )
  
  # ❌ wrong
  raise Exception("bad input")
  ```
- Never silently swallow exceptions.

---

## Domain Patterns

### ODE Right-Hand Side (model.py)

All ODE functions must follow the `scipy.integrate.solve_ivp` signature:

```python
def odes(
    self,
    _time: float,              # prefix _ if unused, keep for solver compat
    state: NDArray[np.float64],
    meal_rate: float,
) -> NDArray[np.float64]:
    """Compute dx/dt for the compartment model."""
    ...
    return np.zeros(3, dtype=np.float64)  # placeholder until SW02
```

State vector convention (always in this order):

```
state[0] – plasma glucose        [mmol/L]
state[1] – plasma insulin        [pmol/L]
state[2] – interstitial glucose  [mmol/L]
```

### Units (always explicit in variable names or docstrings)

| Quantity | Preferred Unit |
| --- | --- |
| Glucose concentration | mmol/L |
| Insulin concentration | pmol/L |
| Time | min |
| Meal glucose | mmol |
| Glucose appearance rate | mmol/min |

Provide conversion functions in `utils.py` rather than inline magic numbers.

### Dataclasses for Data Containers

Use `@dataclass` for parameter sets and result containers:

```python
@dataclass
class SimulationResult:
    time_min: NDArray[np.float64]
    plasma_glucose: NDArray[np.float64]
    cgm_glucose: NDArray[np.float64]
```

---

## Verification Workflow

Run this sequence before every commit:

```
1. black src/ tests/          → auto-formats code (must produce no diff after)
2. pylint src/ tests/         → must score ≥ 9.0/10
3. mypy src/ tests/           → must report 0 errors
4. pytest                     → must pass all tests
```

### Writing Tests

- One test class per module (e.g. `TestGlucoseInsulinModel`).
- Test method names describe the **expected behaviour**: `test_initial_state_shape`.
- Use `pytest.approx` for all floating-point comparisons.
- Test **contracts and structure** now; physiological accuracy tests come in SW10.
- Never test implementation details — test observable behaviour.

```python
# ✅ correct – tests the contract
def test_odes_return_shape(self) -> None:
    """ODE right-hand side must return vector of same shape as state."""
    model = GlucoseInsulinModel()
    dxdt = model.odes(0.0, model.initial_state(), meal_rate=0.0)
    assert dxdt.shape == (3,)

# ❌ wrong – tests internal detail
def test_odes_uses_numpy_zeros(self) -> None:
    ...
```

---

## Prompting Template

When asking Copilot to generate code for this project, use this template:

```
Context:
  - Module: [model.py | simulation.py | utils.py | test_model.py]
  - Current SW milestone: [SW02 | SW03 | ...]
  - Domain: glucose-insulin compartment model, E-DES inspired

Task:
  [Describe what you want in one sentence]

Constraints:
  - Google Python Style Guide (docstrings, naming, type hints)
  - Line length ≤ 79 characters (Black)
  - Units must be documented in docstrings [mmol/L, pmol/L, min]
  - State vector order: [plasma_glucose, plasma_insulin, interstitial_glucose]
  - [Any additional constraint]

Expected output:
  [Function / class / test / module]
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `mypy` complains about `scipy` | Add `# type: ignore[import-untyped]` on the import line |
| Black and pylint disagree on formatting | Black wins — disable the conflicting pylint rule in `.pylintrc` |
| `solve_ivp` returns `success=False` | Check ODE returns correct shape; check initial state is finite |
| Import errors in tests | Ensure `pip install -e .` has been run, or add `src/` to `PYTHONPATH` |