# Quantum BB84 Communication

### Exploring Quantum Key Distribution Using the BB84 Protocol: From Ideal Communication to Noise-Induced Errors

**Team Members:**

- **Sonet D Thomas**
- **Naveen Joy**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.6.0-613394.svg?logo=qiskit&logoColor=white)](https://qiskit.org/)
[![Qiskit Aer](https://img.shields.io/badge/Qiskit--Aer-0.17.2-613394.svg)](https://github.com/Qiskit/qiskit-aer)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Unit%20Tests-9%20Passing-brightgreen.svg)](tests/test_bb84.py)
[![Protocol](https://img.shields.io/badge/Protocol-BB84%20%281984%29-orange.svg)](https://doi.org/10.1016/j.tcs.2014.05.025)

---

## 1. Problem Statement & Proposed Solution

### Problem Statement

To develop a Quantum Key Distribution (QKD) framework using the BB84 protocol, investigate the effects of different noise models, and explore pathways toward reliable and secure quantum communication.

### Proposed Solution

- **Pure Qiskit BB84 Framework**: Built an end-to-end 24-qubit BB84 simulation using **Qiskit** and **Qiskit Aer** to demonstrate how Alice and Bob generate shared random secret keys using conjugate non-orthogonal bases ($Z$ and $X$).
- **Multi-Noise Channel Evaluation**: Systematically modeled and simulated five physical quantum noise channels via Kraus operators at $p = 0.12$:
  1. **Bit Flip ($X$)**: Flips $|0\rangle \leftrightarrow |1\rangle$ in the computational basis.
  2. **Phase Flip ($Z$)**: Inverts superposition phase.
  3. **Bit & Phase Flip ($Y / XZ$)**: Simultaneously perturbs bit and phase.
  4. **Amplitude Damping ($\mathcal{E}_{AD}$)**: Models physical $T_1$ energy relaxation ($|1\rangle \to |0\rangle$) with asymmetric decay, remaining secure for reconciliation.
  5. **Depolarizing Noise**: Uniform isotropic degradation.
- **Shor-Preskill Security Threshold Benchmarking**: Evaluated measured Quantum Bit Error Rate (QBER) against the theoretical **11.0% Shor-Preskill bound**.

```
+---------------------------------------------------------------------------------------------------+
|                                  BB84 PROTOCOL WORKFLOW                                           |
+---------------------------------------------------------------------------------------------------+
|  ALICE (Transmitter)               QUANTUM CHANNEL                BOB (Receiver)                  |
|  -------------------               ---------------                --------------                  |
|  [Random Bit in {0,1}]                                                                            |
|          |                                                                                        |
|  [Random Basis in {Z,X}]                                          [Random Basis in {Z,X}]         |
|          |                                                                      |                 |
|  [Quantum State Prep] ----------> (Qiskit Aer Noise Model) ------> [Measurement Projection]       |
|   |0>, |1>, |+>, |->               Bit Flip, Phase Flip,            In basis beta                 |
|                                    Amplitude Damping, etc.                      |                 |
|                                                                    [Raw Bit Outcome]              |
|                                                                                                   |
|  PUBLIC CLASSICAL CHANNEL:                                                                        |
|  [Basis Sifting] <================== Sift where alpha == beta ==================> [Basis Sifting] |
|  [Sifted Key A]                                                                   [Sifted Key B]  |
|  [Sample Error Check] <============= Sample QBER Estimation ===============> [Sample Error Check] |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Setup & Installation Steps

### Prerequisites

- **Python 3.10+**
- **Git**

### Step-by-Step Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/naveen-joy-18/Quantum-Communication-using-BB84-Protocol.git
cd BB84

# 2. Create an isolated virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Environment

Run this one-line command to verify the installation:

```bash
python -c "import qiskit, qiskit_aer, matplotlib, numpy; print(f'Environment OK: Qiskit {qiskit.__version__} | Aer {qiskit_aer.__version__}')"
```

_Expected output: `Environment OK: Qiskit 2.6.0 | Aer 0.17.2`_

---

## 3. How to Run the Code (Demo Instructions)

### 1. Run Automated Unit Tests (9 Tests)

Verifies protocol logic, basis matching, and all noise models:

```bash
python -m unittest tests/test_bb84.py
```

_Expected output: `Ran 9 tests in ~1.8s ... OK`_

### 2. Run the Full Multi-Noise Simulation Demo

Executes all 6 configurations (Ideal + 5 Noise Channels), outputs side-by-side terminal comparison tables, exports JSON/TXT reports, and generates all visualizations:

```bash
python main.py
```

### 3. Run Individual Noise Channel Demos

Use `--noise-type` to demonstrate any specific channel:

```bash
# Bit & Phase Flip (Y) - Demonstrates Protocol Abort (QBER = 18.18% > 11%)
python main.py --noise-type bit_phase_flip --noise-prob 0.12

# Amplitude Damping - Demonstrates T1 energy decay (|1> -> |0>, QBER = 9.09% <= 11%)
python main.py --noise-type amplitude_damping --noise-prob 0.12

# Bit Flip (X) - Demonstrates Z-basis error with X-basis eigenstate immunity
python main.py --noise-type bit_flip --noise-prob 0.12

# Phase Flip (Z) - Demonstrates X-basis error with Z-basis eigenstate immunity
python main.py --noise-type phase_flip --noise-prob 0.12

# Depolarizing Channel - Demonstrates symmetric degradation
python main.py --noise-type depolarizing --noise-prob 0.12

# Ideal Channel - Demonstrates 100% clean baseline key exchange (QBER = 0%)
python main.py --noise-type none
```

### CLI Options Reference

| Argument         | Type    | Default | Description                                                                                                    |
| ---------------- | ------- | ------- | -------------------------------------------------------------------------------------------------------------- |
| `--qubits`       | `int`   | `24`    | Total number of quantum bits transmitted ($N$)                                                                 |
| `--seed`         | `int`   | `10`    | Random seed for exact reproducibility                                                                          |
| `--noise-prob`   | `float` | `0.12`  | Channel noise parameter ($p$ or $\gamma$)                                                                      |
| `--sample-ratio` | `float` | `0.25`  | Proportion of sifted key checked for QBER estimation                                                           |
| `--noise-type`   | `str`   | `all`   | Channel to run: `all`, `none`, `bit_flip`, `phase_flip`, `bit_phase_flip`, `amplitude_damping`, `depolarizing` |

---

## 4. Explanation of the Output

Running the demo produces three outputs: **Terminal Audit Tables**, **Saved Visualizations (`circuits/`)**, and **Data Reports (`results/`)**.

### 4.1 Terminal Output: Stage-by-Stage Transmission Table

Traces each qubit from Alice's state preparation to Bob's measurement:

```text
---------------------------------------------------------------------------------------------------
 Qubit | Alice Bit | Alice Basis |  State  | Bob Basis | Bob Result | Basis Match? | Sifted Result
---------------------------------------------------------------------------------------------------
   0   |     0     |      Z      |   |0>   |     X     |     0      |   MISMATCH   | -- (Discard)
   3   |     0     |      Z      |   |0>   |     Z     |     0      |  MATCH (OK)  |   0 (Valid)
   4   |     0     |      X      |   |+>   |     X     |     0      |  MATCH (OK)  |   0 (Valid)
  11   |     1     |      Z      |   |1>   |     Z     |     0      |ERROR (NOISE) |   A:1!=B:0
  14   |     1     |      X      |   |->   |     X     |     1      |  MATCH (OK)  |   1 (Valid)
---------------------------------------------------------------------------------------------------
```

- **MISMATCH**: Bases differed (Qubit 0: Alice $Z$, Bob $X$). The state collapses randomly and is discarded. Sifting efficiency is $\approx 50\%$.
- **MATCH (OK)**: Bases matched; transmission succeeded without disturbance.
- **ERROR (NOISE)**: Bases matched, but channel noise corrupted the flying qubit (Qubit 11: Alice sent $|1\rangle$, noise caused relaxation/flip so Bob measured `0`).

### 4.2 Comparative Results Across All Noise Models ($N=24, p=0.12$)

```text
===================================================================================================================
                                    BB84 NOISE MODELS COMPARATIVE SUMMARY
===================================================================================================================
----------------------------------------------------------------------------------------------------------------------------------------------------------
Metric                       |   Ideal Channel    |    Bit Flip (X)    |   Phase Flip (Z)   |  Bit & Phase Flip  | Amplitude Damping  |    Depolarizing
----------------------------------------------------------------------------------------------------------------------------------------------------------
Noise Probability (p)        |        0.00        |        0.12        |        0.12        |        0.12        |        0.12        |        0.12
Transmitted Qubits           |         24         |         24         |         24         |         24         |         24         |         24
Sifted Key Length            |      11 bits       |      11 bits       |      11 bits       |      11 bits       |      11 bits       |      11 bits
Sifting Efficiency           |       45.83%       |       45.83%       |       45.83%       |       45.83%       |       45.83%       |       45.83%
Sample QBER                  |        0.0%        |        0.0%        |        0.0%        |       50.0%        |        0.0%        |        0.0%
Total Sifted QBER            |        0.0%        |       9.09%        |       9.09%        |       18.18%       |       9.09%        |       9.09%
Z-Basis QBER                 |        0.0%        |       16.67%       |        0.0%        |       16.67%       |       16.67%       |       16.67%
X-Basis QBER                 |        0.0%        |        0.0%        |       20.0%        |       20.0%        |        0.0%        |        0.0%
Threshold (11.0%)            |       PASSED       |       PASSED       |       PASSED       |      EXCEEDED      |       PASSED       |       PASSED
Final Key Length             |       9 bits       |       9 bits       |       9 bits       |       9 bits       |       9 bits       |       9 bits
Raw Key Errors               |         0          |         1          |         1          |         1          |         1          |         1
Key Integrity                |    MATCH (100%)    |     RECONCILE      |     RECONCILE      |     RECONCILE      |     RECONCILE      |     RECONCILE
----------------------------------------------------------------------------------------------------------------------------------------------------------
```

### 4.3 Quantum Mechanical Basis Asymmetry

- **Bit Flip ($X$) Asymmetry**: Produces errors in $Z$-basis ($e_Z = 16.7\%$), while $X$-basis states are **immune** ($e_X = 0.0\%$) as eigenstates of $X$.
- **Phase Flip ($Z$) Asymmetry**: Produces errors in $X$-basis ($e_X = 20.0\%$), while $Z$-basis states are **immune** ($e_Z = 0.0\%$) as eigenstates of $Z$.
- **Bit & Phase Flip ($Y / XZ$) Dual Vulnerability**: Disrupts both bases, elevating QBER to **18.18%** and forcing a **Protocol Abort**.
- **Amplitude Damping ($\mathcal{E}_{AD}$)**: Simulates physical $T_1$ energy relaxation ($|1\rangle \to |0\rangle$). Produces asymmetric $Z$-basis decay ($e_Z = 16.7\%$), remaining within the secure ceiling for reconciliation ($9.09\% \le 11.0\%$).

### 4.4 Generated Visual Outputs (`circuits/` folder)

All 20 figures are automatically generated and saved as high-resolution PNG images (300 DPI) in the `circuits/` directory:

| Figure File                                                                                                       | Type              | Description                                                                                  |
| :---------------------------------------------------------------------------------------------------------------- | :---------------- | :------------------------------------------------------------------------------------------- |
| [`bb84_canonical_states.png`](circuits/bb84_canonical_states.png)                                                 | Circuit Primitive | Alice's 4 state preparation circuits: $\|0\rangle, \|1\rangle, \|+\rangle, \|-\rangle$.      |
| [`bb84_basis_combinations.png`](circuits/bb84_basis_combinations.png)                                             | Circuit Primitive | 4 measurement scenarios: deterministic match vs 50/50 state collapse.                        |
| [`bb84_full_circuit.png`](circuits/bb84_full_circuit.png)                                                         | Quantum Circuit   | Complete 24-qubit BB84 transmission circuit (split side-by-side: Part 1 left, Part 2 right). |
| [`bb84_ideal_circuit.png`](circuits/bb84_ideal_circuit.png)                                                       | Quantum Circuit   | Dedicated 24-qubit transmission circuit for the Ideal Channel.                               |
| [`bb84_noisy_circuit.png`](circuits/bb84_noisy_circuit.png)                                                       | Quantum Circuit   | Generic 24-qubit transmission circuit with quantum channel identity/noise gates.             |
| [`bb84_bit_flip_circuit.png`](circuits/bb84_bit_flip_circuit.png)                                                 | Quantum Circuit   | Dedicated 24-qubit transmission circuit for Bit Flip ($X$) noise.                            |
| [`bb84_phase_flip_circuit.png`](circuits/bb84_phase_flip_circuit.png)                                             | Quantum Circuit   | Dedicated 24-qubit transmission circuit for Phase Flip ($Z$) noise.                          |
| [`bb84_bit_phase_flip_circuit.png`](circuits/bb84_bit_phase_flip_circuit.png)                                     | Quantum Circuit   | Dedicated 24-qubit transmission circuit for Bit & Phase Flip ($Y$) noise.                    |
| [`bb84_amplitude_damping_circuit.png`](circuits/bb84_amplitude_damping_circuit.png)                               | Quantum Circuit   | Dedicated 24-qubit transmission circuit for Amplitude Damping ($\mathcal{E}_{AD}$).          |
| [`bb84_depolarizing_circuit.png`](circuits/bb84_depolarizing_circuit.png)                                         | Quantum Circuit   | Dedicated 24-qubit transmission circuit for Depolarizing noise.                              |
| [`key_distribution_analysis.png`](circuits/key_distribution_analysis.png)                                         | Dashboard         | Ideal Channel stages, sifting efficiency pie, basis counts, and 100% key match.              |
| [`bb84_ideal_metrics_analysis.png`](circuits/bb84_ideal_metrics_analysis.png)                                     | Dashboard         | Ideal Channel diagnostics dashboard (clean baseline, 0.0% QBER).                             |
| [`bb84_bit_flip_metrics_analysis.png`](circuits/bb84_bit_flip_metrics_analysis.png)                               | Dashboard         | Bit Flip diagnostics showing $Z$-basis errors and $X$-basis eigenstate immunity.             |
| [`bb84_phase_flip_metrics_analysis.png`](circuits/bb84_phase_flip_metrics_analysis.png)                           | Dashboard         | Phase Flip diagnostics showing $X$-basis errors and $Z$-basis eigenstate immunity.           |
| [`bb84_bit_phase_flip_metrics_analysis.png`](circuits/bb84_bit_phase_flip_metrics_analysis.png)                   | Dashboard         | Bit & Phase Flip diagnostics: QBER ($18.18\%$) vs 11% threshold (Protocol Abort).            |
| [`bb84_amplitude_damping_metrics_analysis.png`](circuits/bb84_amplitude_damping_metrics_analysis.png)             | Dashboard         | Amplitude Damping diagnostics: QBER ($9.09\%$) vs 11% threshold (Secure).                    |
| [`bb84_depolarizing_metrics_analysis.png`](circuits/bb84_depolarizing_metrics_analysis.png)                       | Dashboard         | Depolarizing noise diagnostics dashboard (symmetric error profile).                          |
| [`bb84_noisy_metrics_analysis.png`](circuits/bb84_noisy_metrics_analysis.png)                                     | Dashboard         | Generic noisy channel diagnostics dashboard.                                                 |
| [`bit_phase_flip_and_amplitude_damping_analysis.png`](circuits/bit_phase_flip_and_amplitude_damping_analysis.png) | Comparative Plot  | Side-by-side dashboard directly comparing Bit & Phase Flip vs Amplitude Damping.             |
| [`noise_models_comparison_analysis.png`](circuits/noise_models_comparison_analysis.png)                           | Master Dashboard  | 4-panel comparison of all 6 models, basis error breakdowns, and security decisions.          |

### 4.5 Generated Data Artifacts (`results/` folder)

All 18 numerical summaries and transmission audit reports are stored in the `results/` directory:

- **Consolidated Comparative Reports**:
  - [`bb84_all_noise_models_comparison.json`](results/bb84_all_noise_models_comparison.json): Complete machine-readable JSON payload containing all parameters, sifted keys, basis counts, and QBER metrics across all 6 models.
  - [`bb84_all_noise_models_comparison.txt`](results/bb84_all_noise_models_comparison.txt): Formatted ASCII comparative table for quick terminal/document viewing.
- **Per-Channel Audit Reports & JSON Summaries**:
  - **Ideal Channel**: [`bb84_ideal_run_summary.json`](results/bb84_ideal_run_summary.json) & [`bb84_ideal_detailed_report.txt`](results/bb84_ideal_detailed_report.txt)
  - **Bit Flip ($X$)**: [`bb84_bit_flip_run_summary.json`](results/bb84_bit_flip_run_summary.json) & [`bb84_bit_flip_detailed_report.txt`](results/bb84_bit_flip_detailed_report.txt)
  - **Phase Flip ($Z$)**: [`bb84_phase_flip_run_summary.json`](results/bb84_phase_flip_run_summary.json) & [`bb84_phase_flip_detailed_report.txt`](results/bb84_phase_flip_detailed_report.txt)
  - **Bit & Phase Flip ($Y$)**: [`bb84_bit_phase_flip_run_summary.json`](results/bb84_bit_phase_flip_run_summary.json) & [`bb84_bit_phase_flip_detailed_report.txt`](results/bb84_bit_phase_flip_detailed_report.txt)
  - **Amplitude Damping ($\mathcal{E}_{AD}$)**: [`bb84_amplitude_damping_run_summary.json`](results/bb84_amplitude_damping_run_summary.json) & [`bb84_amplitude_damping_detailed_report.txt`](results/bb84_amplitude_damping_detailed_report.txt)
  - **Depolarizing Channel**: [`bb84_depolarizing_run_summary.json`](results/bb84_depolarizing_run_summary.json) & [`bb84_depolarizing_detailed_report.txt`](results/bb84_depolarizing_detailed_report.txt)
  - **Generic Noisy Run**: [`bb84_noisy_run_summary.json`](results/bb84_noisy_run_summary.json) & [`bb84_noisy_detailed_report.txt`](results/bb84_noisy_detailed_report.txt)
  - **Default Transmission Run**: [`bb84_run_summary.json`](results/bb84_run_summary.json) & [`bb84_detailed_report.txt`](results/bb84_detailed_report.txt)

---

## 5. Repository Structure

```text
BB84/
├── circuits/                                                    # High-resolution visual diagrams (PNG, 300 DPI)
│   ├── bb84_amplitude_damping_circuit.png                      # Dedicated Amplitude Damping transmission circuit (side-by-side)
│   ├── bb84_amplitude_damping_metrics_analysis.png             # Dedicated Amplitude Damping analytics dashboard
│   ├── bb84_basis_combinations.png                             # 4 basis measurement scenarios (deterministic vs collapse)
│   ├── bb84_bit_flip_circuit.png                               # Dedicated Bit Flip transmission circuit (side-by-side)
│   ├── bb84_bit_flip_metrics_analysis.png                      # Dedicated Bit Flip analytics dashboard
│   ├── bb84_bit_phase_flip_circuit.png                         # Dedicated Bit & Phase Flip transmission circuit (side-by-side)
│   ├── bb84_bit_phase_flip_metrics_analysis.png                # Dedicated Bit & Phase Flip analytics dashboard
│   ├── bb84_canonical_states.png                               # Canonical BB84 state preparations (|0>, |1>, |+>, |->)
│   ├── bb84_depolarizing_circuit.png                           # Dedicated Depolarizing transmission circuit (side-by-side)
│   ├── bb84_depolarizing_metrics_analysis.png                  # Dedicated Depolarizing analytics dashboard
│   ├── bb84_full_circuit.png                                   # Complete 24-qubit transmission circuit (Part 1 left, Part 2 right)
│   ├── bb84_ideal_circuit.png                                  # Dedicated Ideal transmission circuit (side-by-side)
│   ├── bb84_ideal_metrics_analysis.png                         # Dedicated Ideal channel analytics dashboard
│   ├── bb84_noisy_circuit.png                                  # Generic noisy transmission circuit (side-by-side)
│   ├── bb84_noisy_metrics_analysis.png                         # Generic noisy channel analytics dashboard
│   ├── bb84_phase_flip_circuit.png                             # Dedicated Phase Flip transmission circuit (side-by-side)
│   ├── bb84_phase_flip_metrics_analysis.png                    # Dedicated Phase Flip analytics dashboard
│   ├── bit_phase_flip_and_amplitude_damping_analysis.png       # Comparative dashboard: Bit & Phase Flip vs Amplitude Damping
│   ├── key_distribution_analysis.png                           # Protocol stage progression and key integrity dashboard
│   └── noise_models_comparison_analysis.png                    # Master 4-panel comparison dashboard across all 6 models
├── results/                                                     # Numerical JSON payloads and transmission audit reports
│   ├── bb84_all_noise_models_comparison.json                   # Consolidated multi-model comparison JSON payload
│   ├── bb84_all_noise_models_comparison.txt                    # Formatted multi-model comparative summary table
│   ├── bb84_amplitude_damping_detailed_report.txt              # Amplitude Damping qubit-by-qubit audit report
│   ├── bb84_amplitude_damping_run_summary.json                 # Amplitude Damping JSON metrics
│   ├── bb84_bit_flip_detailed_report.txt                       # Bit Flip qubit-by-qubit audit report
│   ├── bb84_bit_flip_run_summary.json                          # Bit Flip JSON metrics
│   ├── bb84_bit_phase_flip_detailed_report.txt                 # Bit & Phase Flip qubit-by-qubit audit report
│   ├── bb84_bit_phase_flip_run_summary.json                    # Bit & Phase Flip JSON metrics
│   ├── bb84_depolarizing_detailed_report.txt                   # Depolarizing qubit-by-qubit audit report
│   ├── bb84_depolarizing_run_summary.json                      # Depolarizing JSON metrics
│   ├── bb84_detailed_report.txt                                # Default transmission bit audit report
│   ├── bb84_ideal_detailed_report.txt                          # Ideal channel qubit-by-qubit audit report
│   ├── bb84_ideal_run_summary.json                             # Ideal channel JSON metrics
│   ├── bb84_noisy_detailed_report.txt                          # Noisy channel qubit-by-qubit audit report
│   ├── bb84_noisy_run_summary.json                             # Noisy channel JSON metrics
│   ├── bb84_phase_flip_detailed_report.txt                     # Phase Flip qubit-by-qubit audit report
│   ├── bb84_phase_flip_run_summary.json                        # Phase Flip JSON metrics
│   └── bb84_run_summary.json                                   # Default transmission JSON metrics
├── src/                                                         # Core Python package modules
│   ├── __init__.py                                             # Package initializer
│   ├── bb84_protocol.py                                        # Protocol engine (state prep, noisy quantum channel, sifting, QBER)
│   ├── utils.py                                                # Tabulation, JSON/report exporter, and directory helpers
│   └── visualize.py                                            # Circuit layout (left/right split) and analytics plotting
├── tests/                                                       # Automated testing suite
│   └── test_bb84.py                                            # 9 unit tests verifying all noise models and protocol invariants
├── main.py                                                      # Master CLI entry point (supports --noise-type, sweeps, full demo)
├── requirements.txt                                             # Python dependencies (Qiskit 2.6.0, Qiskit Aer 0.17.2, Matplotlib, NumPy)
└── README.md                                                    # Complete project documentation and reproducibility guide
```
