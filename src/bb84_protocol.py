"""
src/bb84_protocol.py
Implementation of the BB84 Quantum Key Distribution (QKD) Protocol using Qiskit.
Supports Ideal (Noise-Free) and comprehensive Physical Quantum Channel Noise Models:
  1. Bit Flip (X) Noise
  2. Phase Flip (Z) Noise
  3. Bit and Phase Flip (Y / XZ) Noise
  4. Amplitude Damping (Energy Relaxation / Loss) Noise
  5. Depolarizing Channel Noise
"""

import random
from typing import List, Tuple, Dict, Any, Optional
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    pauli_error,
    amplitude_damping_error
)


class BB84Protocol:
    """
    Implements a Quantum Key Distribution (QKD) system using the BB84 protocol
    (Bennett and Brassard, 1984) on Qiskit.
    
    Bases:
      'Z' -> Computational basis (|0>, |1>)
      'X' -> Diagonal/Hadamard basis (|+>, |->)
    """

    SUPPORTED_NOISE_TYPES = [
        "depolarizing",
        "bit_flip",
        "phase_flip",
        "bit_phase_flip",
        "amplitude_damping"
    ]

    def __init__(
        self,
        num_qubits: int = 24,
        seed: Optional[int] = 42,
        noise_prob: float = 0.0,
        noise_type: str = "depolarizing"
    ):
        """
        Initialize the BB84 protocol session.
        :param num_qubits: Number of qubits to transmit from Alice to Bob.
        :param seed: Random seed for reproducibility (optional).
        :param noise_prob: Channel noise probability/parameter (0.0 = ideal noise-free).
        :param noise_type: Channel noise model:
                           - 'bit_flip' (Pauli X)
                           - 'phase_flip' (Pauli Z)
                           - 'bit_phase_flip' (Pauli Y / X followed by Z)
                           - 'amplitude_damping' (decay |1> -> |0>)
                           - 'depolarizing' (isotropic Pauli error)
        """
        self.num_qubits = num_qubits
        self.noise_prob = max(0.0, min(1.0, float(noise_prob)))
        self.noise_type = self._normalize_noise_type(noise_type)
        
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Alice's initial state
        self.alice_bits: List[int] = []
        self.alice_bases: List[str] = []
        
        # Bob's chosen bases and measurements
        self.bob_bases: List[str] = []
        self.bob_results: List[int] = []
        
        # Key sifting and final keys
        self.matching_indices: List[int] = []
        self.alice_sifted_key: List[int] = []
        self.bob_sifted_key: List[int] = []
        
        # Basis-specific error tracking
        self.z_basis_errors: int = 0
        self.z_basis_count: int = 0
        self.x_basis_errors: int = 0
        self.x_basis_count: int = 0
        
        # Verification, QBER & Final shared secret key
        self.sample_indices: List[int] = []
        self.qber: float = 0.0
        self.total_sifted_qber: float = 0.0
        self.final_key_errors: int = 0
        self.is_secure_channel: bool = True
        self.alice_final_key: List[int] = []
        self.bob_final_key: List[int] = []
        
        # Qiskit Circuit, Noise Model and Simulator
        self.circuit: Optional[QuantumCircuit] = None
        self.noise_model: Optional[NoiseModel] = self._build_noise_model()
        self.simulator = AerSimulator(noise_model=self.noise_model) if self.noise_model else AerSimulator()

    def _normalize_noise_type(self, raw_type: str) -> str:
        """Normalizes and maps user noise string to standard noise identifier."""
        t = raw_type.lower().strip().replace("-", "_").replace(" ", "_")
        if t in ["bit_flip", "bit_flip_x", "x"]:
            return "bit_flip"
        elif t in ["phase_flip", "phase_flip_z", "z"]:
            return "phase_flip"
        elif t in ["bit_phase_flip", "bit_and_phase_flip", "y", "xz", "bit_phase"]:
            return "bit_phase_flip"
        elif t in ["amplitude_damping", "amp_damping", "damping"]:
            return "amplitude_damping"
        else:
            return "depolarizing"

    def _build_noise_model(self) -> Optional[NoiseModel]:
        """
        Builds a Qiskit Aer NoiseModel representing the configured physical channel noise:
          - Bit Flip (X)
          - Phase Flip (Z)
          - Bit and Phase Flip (Y / XZ)
          - Amplitude Damping
          - Depolarizing
        """
        if self.noise_prob <= 0.0:
            return None

        nm = NoiseModel()
        p = self.noise_prob

        if self.noise_type == "bit_flip":
            err = pauli_error([("X", p), ("I", 1.0 - p)])
        elif self.noise_type == "phase_flip":
            err = pauli_error([("Z", p), ("I", 1.0 - p)])
        elif self.noise_type == "bit_phase_flip":
            err_x = pauli_error([("X", p), ("I", 1.0 - p)])
            err_z = pauli_error([("Z", p), ("I", 1.0 - p)])
            err = err_x.compose(err_z)
        elif self.noise_type == "amplitude_damping":
            err = amplitude_damping_error(p)
        else:  # "depolarizing"
            err = depolarizing_error(p, 1)

        # Apply noise to the channel propagation (id gate)
        nm.add_all_qubit_quantum_error(err, ["id"])
        return nm

    def generate_alice_bits_and_bases(self) -> Tuple[List[int], List[str]]:
        """
        Alice generates random classical bits and random encoding bases.
        'Z' = Rectilinear/Computational basis, 'X' = Diagonal/Hadamard basis.
        """
        self.alice_bits = [random.choice([0, 1]) for _ in range(self.num_qubits)]
        self.alice_bases = [random.choice(["Z", "X"]) for _ in range(self.num_qubits)]
        return self.alice_bits, self.alice_bases

    def generate_bob_bases(self) -> List[str]:
        """
        Bob independently generates random measurement bases.
        """
        self.bob_bases = [random.choice(["Z", "X"]) for _ in range(self.num_qubits)]
        return self.bob_bases

    def get_state_symbol(self, bit: int, basis: str) -> str:
        """Returns the ket representation of the state."""
        if basis == "Z":
            return "|0>" if bit == 0 else "|1>"
        else:  # basis == 'X'
            return "|+>" if bit == 0 else "|->"

    def build_full_circuit(self) -> QuantumCircuit:
        """
        Constructs the multi-qubit Qiskit quantum circuit representing the BB84 transmission:
        1. Alice State Preparation (X and H gates)
        2. Quantum Channel Propagation (id gates with barrier)
        3. Bob Measurement Basis Selection (H gate for X-basis)
        4. Bob Measurement into classical register
        """
        qc_name = f"BB84_{self.noise_type.title()}_Protocol" if self.noise_prob > 0 else "BB84_Ideal_Protocol"
        qc = QuantumCircuit(self.num_qubits, self.num_qubits, name=qc_name)

        # 1. Alice State Preparation
        for i in range(self.num_qubits):
            bit = self.alice_bits[i]
            basis = self.alice_bases[i]
            
            # If bit is 1, apply X gate to flip |0> to |1>
            if bit == 1:
                qc.x(i)
            # If basis is X, apply Hadamard gate
            if basis == "X":
                qc.h(i)
        
        # 2. Quantum Channel Propagation
        for i in range(self.num_qubits):
            qc.id(i)
        qc.barrier(label="Quantum Channel")

        # 3. Bob's Measurement Basis Setup
        for i in range(self.num_qubits):
            # If Bob chooses X basis, rotate to Z basis using H gate before measurement
            if self.bob_bases[i] == "X":
                qc.h(i)
            # Measure qubit i into classical bit i
            qc.measure(i, i)

        self.circuit = qc
        return qc

    def run_simulation(self) -> List[int]:
        """
        Executes the quantum circuit on Qiskit AerSimulator (with channel noise if configured).
        Retrieves Bob's measured classical bits.
        """
        if self.circuit is None:
            self.build_full_circuit()

        # Update noise model if changed
        self.noise_model = self._build_noise_model()
        if self.noise_model:
            self.simulator = AerSimulator(noise_model=self.noise_model)
        else:
            self.simulator = AerSimulator()

        # Transpile with optimization_level=0 to keep id gate channel representation
        compiled_circuit = transpile(self.circuit, self.simulator, optimization_level=0)
        
        # Single shot simulation represents real single-photon transmission
        run_kwargs = {"shots": 1, "memory": True}
        if self.seed is not None:
            run_kwargs["seed_simulator"] = self.seed
        job = self.simulator.run(compiled_circuit, **run_kwargs)
        result = job.result()
        
        # In Qiskit, bitstring memory is formatted with qubit n-1 at index 0 (little-endian)
        # We reverse it to match qubit 0 .. num_qubits-1 indexing
        memory = result.get_memory()[0]
        self.bob_results = [int(b) for b in reversed(memory)]
        return self.bob_results

    def perform_sifting(self) -> Tuple[List[int], List[int]]:
        """
        Alice and Bob communicate classically to compare their bases.
        Bits where Alice's basis == Bob's basis are retained in the sifted key.
        Bits where bases differed are discarded.
        Also computes basis-specific error breakdown (Z-basis vs X-basis).
        """
        self.matching_indices = []
        self.alice_sifted_key = []
        self.bob_sifted_key = []
        self.z_basis_errors = 0
        self.z_basis_count = 0
        self.x_basis_errors = 0
        self.x_basis_count = 0

        for i in range(self.num_qubits):
            if self.alice_bases[i] == self.bob_bases[i]:
                self.matching_indices.append(i)
                self.alice_sifted_key.append(self.alice_bits[i])
                self.bob_sifted_key.append(self.bob_results[i])
                
                # Check basis-specific behavior
                is_error = (self.alice_bits[i] != self.bob_results[i])
                if self.alice_bases[i] == "Z":
                    self.z_basis_count += 1
                    if is_error:
                        self.z_basis_errors += 1
                else:
                    self.x_basis_count += 1
                    if is_error:
                        self.x_basis_errors += 1

        return self.alice_sifted_key, self.bob_sifted_key

    def verify_key_and_estimate_qber(self, sample_ratio: float = 0.25) -> Tuple[float, List[int], List[int]]:
        """
        Alice and Bob estimate the Quantum Bit Error Rate (QBER) by comparing a random sample
        of their sifted key over the classical channel.
        
        In normal communication without eavesdropping/noise, QBER is 0.0%.
        Under channel noise, QBER measures the fraction of errors.
        Theoretical BB84 security limit is 11.0% QBER.
        The sampled bits are discarded to prevent eavesdroppers from discovering them.
        The remaining bits form the final secret key.
        """
        sifted_length = len(self.alice_sifted_key)
        if sifted_length == 0:
            self.qber = 0.0
            self.total_sifted_qber = 0.0
            self.final_key_errors = 0
            self.is_secure_channel = True
            self.alice_final_key = []
            self.bob_final_key = []
            return 0.0, [], []

        # Calculate true total sifted error rate across all matching bits
        sifted_errors = sum(1 for a, b in zip(self.alice_sifted_key, self.bob_sifted_key) if a != b)
        self.total_sifted_qber = (sifted_errors / sifted_length) * 100.0

        # Determine number of sample bits to test (at least 1 if sifted_length >= 2)
        sample_count = max(1, int(sifted_length * sample_ratio))
        if sample_count >= sifted_length and sifted_length > 1:
            sample_count = sifted_length - 1

        # Select random indices from the sifted key
        all_sifted_indices = list(range(sifted_length))
        self.sample_indices = sorted(random.sample(all_sifted_indices, sample_count))

        # Check errors in sample
        sample_errors = 0
        for idx in self.sample_indices:
            if self.alice_sifted_key[idx] != self.bob_sifted_key[idx]:
                sample_errors += 1
        
        self.qber = (sample_errors / sample_count) * 100.0
        self.is_secure_channel = (self.qber <= 11.0)

        # Construct final key by excluding the sampled bits
        sample_set = set(self.sample_indices)
        self.alice_final_key = [
            self.alice_sifted_key[i] for i in range(sifted_length) if i not in sample_set
        ]
        self.bob_final_key = [
            self.bob_sifted_key[i] for i in range(sifted_length) if i not in sample_set
        ]

        # Count bit errors remaining in the raw final key
        self.final_key_errors = sum(1 for a, b in zip(self.alice_final_key, self.bob_final_key) if a != b)

        return self.qber, self.alice_final_key, self.bob_final_key

    def get_summary_data(self) -> Dict[str, Any]:
        """Returns structured metrics and information about the BB84 session."""
        keys_match = (self.alice_final_key == self.bob_final_key) and len(self.alice_final_key) > 0
        sifting_efficiency = (len(self.alice_sifted_key) / self.num_qubits) * 100.0 if self.num_qubits > 0 else 0.0
        
        z_qber = (self.z_basis_errors / self.z_basis_count * 100.0) if self.z_basis_count > 0 else 0.0
        x_qber = (self.x_basis_errors / self.x_basis_count * 100.0) if self.x_basis_count > 0 else 0.0

        return {
            "total_qubits_sent": self.num_qubits,
            "noise_prob": self.noise_prob,
            "noise_type": self.noise_type,
            "is_noisy": self.noise_prob > 0.0,
            "sifted_key_length": len(self.alice_sifted_key),
            "sifting_efficiency_percent": round(sifting_efficiency, 2),
            "sample_verification_size": len(self.sample_indices),
            "qber_percent": round(self.qber, 2),
            "total_sifted_qber_percent": round(self.total_sifted_qber, 2),
            "z_basis_count": self.z_basis_count,
            "z_basis_errors": self.z_basis_errors,
            "z_basis_qber_percent": round(z_qber, 2),
            "x_basis_count": self.x_basis_count,
            "x_basis_errors": self.x_basis_errors,
            "x_basis_qber_percent": round(x_qber, 2),
            "bb84_threshold_percent": 11.0,
            "security_status": "SECURE (QBER <= 11.0% BB84 threshold)" if self.is_secure_channel else "INSECURE / ABORT (QBER > 11.0% threshold)",
            "final_key_length": len(self.alice_final_key),
            "final_key_errors": self.final_key_errors,
            "keys_match": keys_match,
            "alice_bits": self.alice_bits,
            "alice_bases": self.alice_bases,
            "alice_states": [self.get_state_symbol(b, base) for b, base in zip(self.alice_bits, self.alice_bases)],
            "bob_bases": self.bob_bases,
            "bob_results": self.bob_results,
            "matching_basis_mask": [self.alice_bases[i] == self.bob_bases[i] for i in range(self.num_qubits)],
            "alice_sifted_key": self.alice_sifted_key,
            "bob_sifted_key": self.bob_sifted_key,
            "alice_final_key": "".join(map(str, self.alice_final_key)),
            "bob_final_key": "".join(map(str, self.bob_final_key))
        }
