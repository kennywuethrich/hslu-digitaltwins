# HSLU TA.DIGITALTWIN – Glucose-Insulin Digital Twin

Semester project for the module **TA.DIGITALTWIN – Digital Twins and Products**
at Hochschule Luzern, Technik & Architektur.

## Project Goal

Model the effect of a meal on **blood glucose and insulin levels** using a
low-order grey-box compartment model (E-DES).  
A CGM (Continuous Glucose Monitoring) patch measures interstitial glucose as
the system output.

```
Input:  meal glucose equivalent  [mmol]
Output: interstitial glucose     [mmol/L]  (CGM measurement)
```

## Semester Roadmap

| SW  | Milestone |
|-----|-----------|
| SW02 | Model Specification & Block Diagram |
| SW03 | DT Requirements & System Decomposition (5D) |
| SW04 | State Machine (insulin pump), Behaviour Models (meal, activity) |
| SW08 | Insulin Pump Use Case |
| SW10 | State Estimation, Model Validation, Personalisation |
| SW11 | Data Architecture |
| SW12 | Full 5D Digital Twin Integration |

## Setup

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

## Project Structure

```
src/glucose_insulin/
    __init__.py       – package entry point
    model.py          – ODE compartment model (E-DES skeleton)
    simulation.py     – simulation runner & result dataclass
    utils.py          – unit conversion and helper functions
tests/
    test_model.py     – unit tests for the model
```

## Code Style

Google Python Style Guide · Black (line-length 79) · mypy strict · pylint
