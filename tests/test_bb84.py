"""
tests/test_bb84.py
Comprehensive unit tests for BB84 Protocol implementation using Qiskit.
Tests both Ideal Channel and Physical Quantum Channel Noise Models:
  1. Ideal (Noise-Free) Channel
  2. Bit Flip (X) Noise Channel
  3. Phase Flip (Z) Noise Channel
  4. Bit and Phase Flip (Y / XZ) Noise Channel
  5. Amplitude Damping Noise Channel
  6. Depolarizing Noise Channel
"""

import unittest
from src.bb84_protocol import BB84Protocol


class TestBB84Protocol(unittest.TestCase):

    def setUp(self):
        self.num_qubits = 24
        self.ideal_protocol = BB84Protocol(num_qubits=self.num_qubits, seed=123, noise_prob=0.0)

    def test_bit_and_basis_generation(self):
        bits, bases = self.ideal_protocol.generate_alice_bits_and_bases()
        self.assertEqual(len(bits), self.num_qubits)
        self.assertEqual(len(bases), self.num_qubits)
        self.assertTrue(all(b in [0, 1] for b in bits))
        self.assertTrue(all(base in ['Z', 'X'] for base in bases))

        bob_bases = self.ideal_protocol.generate_bob_bases()
        self.assertEqual(len(bob_bases), self.num_qubits)
        self.assertTrue(all(base in ['Z', 'X'] for base in bob_bases))

    def test_ideal_circuit_construction_and_simulation(self):
        self.ideal_protocol.generate_alice_bits_and_bases()
        self.ideal_protocol.generate_bob_bases()
        qc = self.ideal_protocol.build_full_circuit()
        self.assertEqual(qc.num_qubits, self.num_qubits)
        self.assertEqual(qc.num_clbits, self.num_qubits)

        bob_results = self.ideal_protocol.run_simulation()
        self.assertEqual(len(bob_results), self.num_qubits)
        self.assertTrue(all(res in [0, 1] for res in bob_results))

    def test_ideal_sifting_deterministic_match(self):
        """
        In an ideal channel, matching bases must produce 100% deterministic agreement.
        """
        self.ideal_protocol.generate_alice_bits_and_bases()
        self.ideal_protocol.generate_bob_bases()
        self.ideal_protocol.build_full_circuit()
        self.ideal_protocol.run_simulation()

        alice_sifted, bob_sifted = self.ideal_protocol.perform_sifting()
        self.assertEqual(len(alice_sifted), len(bob_sifted))
        self.assertEqual(alice_sifted, bob_sifted)

    def test_ideal_qber_and_final_key(self):
        """
        Under normal noise-free conditions, QBER must be 0%.
        """
        self.ideal_protocol.generate_alice_bits_and_bases()
        self.ideal_protocol.generate_bob_bases()
        self.ideal_protocol.build_full_circuit()
        self.ideal_protocol.run_simulation()
        self.ideal_protocol.perform_sifting()

        qber, alice_final, bob_final = self.ideal_protocol.verify_key_and_estimate_qber(sample_ratio=0.25)
        self.assertEqual(qber, 0.0)
        self.assertEqual(alice_final, bob_final)
        self.assertTrue(len(alice_final) > 0)

    def test_bit_flip_x_noise_channel(self):
        """
        Bit Flip (X) noise flips bits in the Z-basis (|0> <-> |1>),
        while leaving X-basis states (|+>, |->) unaltered.
        """
        proto = BB84Protocol(num_qubits=24, seed=10, noise_prob=0.25, noise_type="bit_flip")
        self.assertEqual(proto.noise_type, "bit_flip")
        self.assertIsNotNone(proto.noise_model)

        proto.generate_alice_bits_and_bases()
        proto.generate_bob_bases()
        proto.build_full_circuit()
        proto.run_simulation()
        proto.perform_sifting()
        proto.verify_key_and_estimate_qber(sample_ratio=0.25)

        summary = proto.get_summary_data()
        self.assertTrue(summary["is_noisy"])
        self.assertGreater(summary["z_basis_errors"], 0)
        self.assertEqual(summary["x_basis_errors"], 0)

    def test_phase_flip_z_noise_channel(self):
        """
        Phase Flip (Z) noise flips bits in the X-basis (|+> <-> |->),
        while leaving Z-basis states (|0>, |1>) unaltered.
        """
        proto = BB84Protocol(num_qubits=24, seed=10, noise_prob=0.25, noise_type="phase_flip")
        self.assertEqual(proto.noise_type, "phase_flip")
        self.assertIsNotNone(proto.noise_model)

        proto.generate_alice_bits_and_bases()
        proto.generate_bob_bases()
        proto.build_full_circuit()
        proto.run_simulation()
        proto.perform_sifting()
        proto.verify_key_and_estimate_qber(sample_ratio=0.25)

        summary = proto.get_summary_data()
        self.assertTrue(summary["is_noisy"])
        self.assertEqual(summary["z_basis_errors"], 0)
        self.assertGreater(summary["x_basis_errors"], 0)

    def test_bit_and_phase_flip_noise_channel(self):
        """
        Bit and Phase Flip (Y / XZ) noise causes errors in the sifted key.
        """
        proto = BB84Protocol(num_qubits=24, seed=10, noise_prob=0.25, noise_type="bit_phase_flip")
        self.assertEqual(proto.noise_type, "bit_phase_flip")
        self.assertIsNotNone(proto.noise_model)

        proto.generate_alice_bits_and_bases()
        proto.generate_bob_bases()
        proto.build_full_circuit()
        proto.run_simulation()
        proto.perform_sifting()
        proto.verify_key_and_estimate_qber(sample_ratio=0.25)

        self.assertGreater(proto.total_sifted_qber, 0.0)

    def test_amplitude_damping_noise_channel(self):
        """
        Amplitude Damping noise models energy dissipation / photon loss (|1> -> |0>).
        """
        proto = BB84Protocol(num_qubits=24, seed=10, noise_prob=0.30, noise_type="amplitude_damping")
        self.assertEqual(proto.noise_type, "amplitude_damping")
        self.assertIsNotNone(proto.noise_model)

        proto.generate_alice_bits_and_bases()
        proto.generate_bob_bases()
        proto.build_full_circuit()
        proto.run_simulation()
        proto.perform_sifting()
        proto.verify_key_and_estimate_qber(sample_ratio=0.25)

        summary = proto.get_summary_data()
        self.assertTrue(summary["is_noisy"])
        self.assertGreater(summary["total_sifted_qber_percent"], 0.0)

    def test_depolarizing_channel_metrics(self):
        """
        Depolarizing channel noise introduces symmetric Pauli errors.
        """
        proto = BB84Protocol(num_qubits=28, seed=123, noise_prob=0.25, noise_type="depolarizing")
        proto.generate_alice_bits_and_bases()
        proto.generate_bob_bases()
        proto.build_full_circuit()
        proto.run_simulation()
        proto.perform_sifting()
        proto.verify_key_and_estimate_qber(sample_ratio=0.25)

        summary = proto.get_summary_data()
        self.assertTrue(summary["is_noisy"])
        self.assertIn("bb84_threshold_percent", summary)
        self.assertIn("security_status", summary)


if __name__ == "__main__":
    unittest.main()
