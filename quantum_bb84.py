# quantum_bb84.py
# Quantum Key Distribution using the BB84 Protocol
# CS 5250 Advanced Computer Architecture — Final Project
# Mihail Chitorog

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import random

# ─────────────────────────────────────────────
# HELPER: Run a circuit and get a single result
# ─────────────────────────────────────────────
def measure_circuit(qc):
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    return list(counts.keys())[0]  # single bitstring result

# ─────────────────────────────────────────────
# STEP 1: Alice prepares a qubit
# ─────────────────────────────────────────────
def alice_prepare_qubit(bit, basis):
    """
    Alice encodes one classical bit into a qubit.

    Two bases available (think of them as two different 'languages'):
      + basis (rectilinear): 0 = |0⟩, 1 = |1⟩
      × basis (diagonal):   0 = |+⟩, 1 = |−⟩

    If Bob measures in the SAME basis Alice used → correct result.
    If Bob measures in a DIFFERENT basis → random garbage (50/50).
    This is the heart of BB84.
    """
    qc = QuantumCircuit(1, 1)

    if bit == 1:
        qc.x(0)          # Flip to |1⟩

    if basis == 'x':     # Diagonal basis
        qc.h(0)          # Hadamard puts it into diagonal superposition

    return qc

# ─────────────────────────────────────────────
# STEP 2: Bob measures a qubit
# ─────────────────────────────────────────────
def bob_measure(qc, basis):
    """
    Bob picks a random basis to measure in.
    If he matches Alice's basis → gets the correct bit.
    If he doesn't → gets a random bit (useless).
    """
    qc = qc.copy()

    if basis == 'x':     # To measure in diagonal basis, apply H first
        qc.h(0)

    qc.measure(0, 0)
    result = measure_circuit(qc)
    return int(result)

# ─────────────────────────────────────────────
# STEP 3: Eve intercepts (optional)
# ─────────────────────────────────────────────
def eve_intercept(qc):
    """
    Eve tries to read the qubit in transit.
    Problem: she doesn't know Alice's basis, so she guesses randomly.
    When she guesses wrong, she DISTURBS the qubit irreversibly.
    Alice and Bob will detect this as unusual errors.

    This is the quantum no-cloning theorem in action:
    Eve cannot copy the qubit without disturbing it.
    """
    eve_basis = random.choice(['+', 'x'])
    qc_copy = qc.copy()

    if eve_basis == 'x':
        qc_copy.h(0)

    qc_copy.measure(0, 0)
    measure_circuit(qc_copy)  # Eve reads it (and disturbs it)

    # Eve resends her best guess — but damage is done
    eve_resend = QuantumCircuit(1, 1)
    if eve_basis == 'x':
        eve_resend.h(0)

    return eve_resend  # Corrupted qubit sent to Bob

# ─────────────────────────────────────────────
# MAIN SIMULATION
# ─────────────────────────────────────────────
def run_bb84(num_bits=20, eve_present=False):
    print("=" * 55)
    print("       BB84 Quantum Key Distribution Protocol")
    print("=" * 55)
    print(f"  Simulating {num_bits} qubits | Eve present: {eve_present}")
    print("=" * 55)

    # Alice generates random bits and random bases
    alice_bits   = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases  = [random.choice(['+', 'x']) for _ in range(num_bits)]

    # Bob randomly chooses his measurement bases
    bob_bases    = [random.choice(['+', 'x']) for _ in range(num_bits)]
    bob_results  = []

    print("\n[1] Alice sends qubits to Bob...")
    if eve_present:
        print("    !!!  Eve is intercepting the channel!\n")

    for i in range(num_bits):
        # Alice prepares qubit
        qc = alice_prepare_qubit(alice_bits[i], alice_bases[i])

        # Eve intercepts if present
        if eve_present:
            qc = eve_intercept(qc)

        # Bob measures
        result = bob_measure(qc, bob_bases[i])
        bob_results.append(result)

    # ─────────────────────────────────────────
    # STEP 4: Sifting — keep only matching bases
    # ─────────────────────────────────────────
    print("[2] Alice and Bob compare bases publicly...")
    print("    (They only reveal WHICH basis, never the actual bits)\n")

    sifted_alice = []
    sifted_bob   = []
    matching_indices = []

    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])
            matching_indices.append(i)

    print(f"    Matching bases: {len(matching_indices)}/{num_bits} bits kept")

    # ─────────────────────────────────────────
    # STEP 5: Error checking — detect Eve
    # ─────────────────────────────────────────
    print("\n[3] Checking for eavesdropping...")
    check_size = min(4, len(sifted_alice))  # Sacrifice a few bits to check
    errors = 0

    for i in range(check_size):
        if sifted_alice[i] != sifted_bob[i]:
            errors += 1

    error_rate = errors / check_size if check_size > 0 else 0
    print(f"    Error rate in sample: {errors}/{check_size} = {error_rate:.0%}")

    # ─────────────────────────────────────────
    # STEP 6: Final shared key
    # ─────────────────────────────────────────
    # Use remaining bits (after sacrificing check bits) as the key
    final_key_alice = sifted_alice[check_size:]
    final_key_bob   = sifted_bob[check_size:]

    print("\n[4] Final Results:")
    print(f"    Alice's key : {final_key_alice}")
    print(f"    Bob's key   : {final_key_bob}")

    keys_match = final_key_alice == final_key_bob

    if error_rate > 0.15:
        print("\n  !!! HIGH ERROR RATE DETECTED — Eve is likely eavesdropping!")
        print("     Alice and Bob discard this key and start over.")
    elif keys_match:
        print("\n  ! Keys match! Secure channel established.")
        print(f"     Shared secret key: {final_key_alice}")
        key_int = int(''.join(map(str, final_key_alice)), 2) if final_key_alice else 0
        print(f"     As a number: {key_int}")
    else:
        print("\n  !!!  Keys don't match — transmission error or Eve detected.")

    return final_key_alice, error_rate

# ─────────────────────────────────────────────
# STEP 7: Visualize error rates with/without Eve
# ─────────────────────────────────────────────
def visualize_eve_detection(trials=10):
    """
    Run multiple trials with and without Eve.
    Show that Eve's presence is statistically detectable.
    """
    print("\n" + "=" * 55)
    print("  Running", trials, "trials to visualize Eve detection...")
    print("=" * 55)

    no_eve_errors   = []
    with_eve_errors = []

    for _ in range(trials):
        _, err_no_eve   = run_bb84(num_bits=20, eve_present=False)
        _, err_with_eve = run_bb84(num_bits=20, eve_present=True)
        no_eve_errors.append(err_no_eve)
        with_eve_errors.append(err_with_eve)

    avg_no_eve   = sum(no_eve_errors)   / trials
    avg_with_eve = sum(with_eve_errors) / trials

    print(f"\n  Average error rate WITHOUT Eve : {avg_no_eve:.0%}")
    print(f"  Average error rate WITH Eve    : {avg_with_eve:.0%}")
    print(f"\n  Theory predicts ~0% without Eve, ~25% with Eve.")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(['Without Eve', 'With Eve'],
           [avg_no_eve, avg_with_eve],
           color=['steelblue', 'crimson'],
           width=0.4)
    ax.axhline(y=0.25, color='orange', linestyle='--', label='Theoretical 25% threshold')
    ax.set_ylabel('Average Error Rate')
    ax.set_title('BB84: Eve Detection via Error Rate\n(Quantum Eavesdropping Detection)')
    ax.set_ylim(0, 0.6)
    ax.legend()
    plt.tight_layout()
    plt.savefig('bb84_eve_detection.png', dpi=150)
    plt.show()
    print("\n  Chart saved as bb84_eve_detection.png")

# ─────────────────────────────────────────────
# RUN EVERYTHING
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  SCENARIO 1: Normal transmission (no eavesdropper)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    run_bb84(num_bits=20, eve_present=False)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  SCENARIO 2: Eve is intercepting the channel")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    run_bb84(num_bits=20, eve_present=True)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  SCENARIO 3: Statistical Eve detection across trials")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    visualize_eve_detection(trials=10)
