# quantum_rng.py
# Quantum Random Number Generator using IBM Qiskit
# CS 5250 Final Project — Mihail Chitorog

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def quantum_random_number(num_bits=8):
    """
    Generate a truly random number using quantum superposition.
    
    A classic computers use pseudo-random algorithms (deterministic).
    A qubit in superposition has NO predetermined outcome. It is
    genuinely 50/50 until measured. This is TRUE randomness.
    """
    
    # Create a circuit with num_bits qubits and num_bits classical bits
    qc = QuantumCircuit(num_bits, num_bits)
    
    # Apply Hadamard gate to every qubit
    # H gate puts qubit into superposition: |0⟩ → (|0⟩ + |1⟩)/√2
    # Before measurement, the qubit is BOTH 0 and 1 simultaneously
    for i in range(num_bits):
        qc.h(i)
    
    # Measure all qubits → collapses superposition to 0 or 1
    qc.measure(range(num_bits), range(num_bits))
    
    return qc

def run_and_display(num_bits=8, shots=1024):
    """
    Running the circuit on a local quantum simulator and display results.
    shots = how many times we repeat the experiment
    """
    
    qc = quantum_random_number(num_bits)
    
    # Draw the circuit so we can see it
    print("=== Quantum Circuit ===")
    print(qc.draw(output='text'))
    
    # Use local Aer simulator 
    simulator = AerSimulator()
    
    # Run the circuit
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Pick one random result and convert binary → integer
    # In a real run, each shot gives a different random bitstring
    sample_bitstring = list(counts.keys())[0]
    random_number = int(sample_bitstring, 2)
    
    print(f"\n=== Results ({shots} shots) ===")
    print(f"Sample random number (0–{2**num_bits - 1}): {random_number}")
    print(f"All measurement outcomes: {len(counts)} unique values")
    print(f"\nTop 5 outcomes:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for bitstring, count in sorted_counts[:5]:
        print(f"  |{bitstring}⟩ → {int(bitstring,2):3d}  ({count} times)")
    
    # Plot histogram of results
    fig = plot_histogram(counts, title="Quantum Random Number Distribution")
    plt.tight_layout()
    plt.savefig("quantum_rng_histogram.png", dpi=150)
    plt.show()
    print("\nHistogram saved as quantum_rng_histogram.png")
    
    return random_number, counts

def compare_classical_vs_quantum():
    """
    Showing the conceptual difference for the presentation.
    Classical: deterministic algorithm pretending to be random.
    Quantum: genuinely non-deterministic at the physics level.
    """
    import random
    
    print("=== Classical RNG (pseudo-random) ===")
    print("Uses a seed + math formula. Given same seed → SAME sequence always.")
    random.seed(42)
    classical = [random.randint(0, 255) for _ in range(5)]
    print(f"Seed 42 → {classical}")
    random.seed(42)
    classical_repeat = [random.randint(0, 255) for _ in range(5)]
    print(f"Seed 42 again → {classical_repeat}  ← identical!")
    
    print("\n=== Quantum RNG (truly random) ===")
    print("No seed. No formula. Physics itself decides.")
    print("Running quantum circuit...")
    num, _ = run_and_display(num_bits=8, shots=5)
    print("Each run produces a genuinely different outcome.")

if __name__ == "__main__":
    compare_classical_vs_quantum()