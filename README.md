# CS 5250 Final Project — Quantum Key Distribution on IBM Quantum Hardware
**Mihail Chitorog | Cal Poly | CS 5250 Advanced Computer Architecture**

## Overview
This project implements the BB84 Quantum Key Distribution (QKD) protocol 
using IBM's Qiskit framework, run on a real 156-qubit IBM quantum computer (ibm_fez).
It also includes a Quantum Random Number Generator to demonstrate true quantum randomness.

## Programs
- `quantum_rng.py` — Quantum Random Number Generator using superposition
- `quantum_bb84_ibm.py` — BB84 QKD protocol running on real IBM quantum hardware

## Key Concepts Demonstrated
- Qubits, superposition, and the Hadamard gate
- Quantum measurement and wave function collapse
- The no-cloning theorem
- Eavesdropping detection via error rate analysis
- True quantum randomness vs. classical pseudo-randomness

## Results
- Scenario 1 (No Eve): 0% error rate — secure key established
- Scenario 2 (Eve present): 33% error rate — eavesdropper detected

## Setup
```bash
conda create -n quantum python=3.11
conda activate quantum
pip install qiskit qiskit-ibm-runtime qiskit-aer matplotlib pylatexenc
```

## Presentation
YouTube: https://www.youtube.com/watch?v=i4ofZGBaRTc
