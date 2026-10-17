"""
main.py
Comprehensive execution entry point for BB84 Quantum Key Distribution (QKD) using Qiskit.
Simulates:
  1. Ideal (Noise-Free) Channel
  2. Bit Flip (X) Noise Channel
  3. Phase Flip (Z) Noise Channel
  4. Bit and Phase Flip (Y / XZ) Noise Channel
  5. Amplitude Damping (Energy Loss) Noise Channel
  6. Depolarizing Noise Channel
Measures identical metrics across all models, saves circuit images, and exports detailed reports.
"""

import os
import argparse
from typing import Dict, Any
from src.bb84_protocol import BB84Protocol
from src.visualize import (
    generate_all_visualizations,
    save_all_noise_models_comparison_image,
    save_multi_noise_sweep_image,
    save_bit_phase_flip_and_amplitude_damping_analysis
)
from src.utils import (
    format_protocol_table,
    export_results,
    format_multi_noise_comparison_table,
    export_multi_noise_comparison
)


def run_single_session(
    num_qubits: int,
    seed: int,
    noise_prob: float,
    noise_type: str,
    sample_ratio: float,
    circuits_dir: str,
    results_dir: str,
    prefix: str,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Executes a single BB84 session under a specified noise model and saves its outputs.
    """
    is_noisy = noise_prob > 0.0 and noise_type != "none"
    label = f"{noise_type.upper().replace('_', ' ')} CHANNEL (p={noise_prob})" if is_noisy else "IDEAL / NORMAL CHANNEL (Noise-Free)"

    if verbose:
        print("\n" + "=" * 85)
        print(f"      BB84 QKD SIMULATION: {label}")
        print("=" * 85)
        print(f"[*] Configuration: Qubits = {num_qubits}, Seed = {seed}, Sample Ratio = {sample_ratio * 100:.0f}%")
        print(f"[*] Channel Noise: {'None (Ideal)' if not is_noisy else f'{noise_type} with p = {noise_prob}'}\n")

    # 1. Initialize Protocol
    protocol = BB84Protocol(num_qubits=num_qubits, seed=seed, noise_prob=noise_prob if is_noisy else 0.0, noise_type=noise_type)

    # 2. Alice generates random bits and bases
    alice_bits, alice_bases = protocol.generate_alice_bits_and_bases()

    # 3. Bob selects random bases
    bob_bases = protocol.generate_bob_bases()

    # 4. Construct Quantum Circuit & Transmit across Quantum Channel
    protocol.build_full_circuit()
    bob_results = protocol.run_simulation()

    # 5. Sifting Phase
    alice_sifted, bob_sifted = protocol.perform_sifting()

    # 6. Parameter Estimation & QBER
    qber, alice_final, bob_final = protocol.verify_key_and_estimate_qber(sample_ratio=sample_ratio)

    summary = protocol.get_summary_data()

    if verbose:
        sift_eff = summary["sifting_efficiency_percent"]
        print(f"[1] Alice generated {num_qubits} qubits in random bases (Z and X).")
        print(f"[2] Bob measured in independent random bases.")
        print(f"[3] Quantum Circuit simulated with Qiskit Aer ({'Noisy Model' if is_noisy else 'Ideal Simulator'}).")
        print(f"[4] Sifting: {len(alice_sifted)}/{num_qubits} matching bases ({sift_eff}%).")
        print(f"[5] QBER Verification: Measured Sample QBER = {qber:.2f}%, Total Sifted QBER = {protocol.total_sifted_qber:.2f}%.")
        print(f"[6] Threshold (11.0%): {'PASSED (Channel Secure)' if protocol.is_secure_channel else 'EXCEEDED (Channel Insecure/Abort)'}.")
        print(f"[7] Final Key: Alice = {''.join(map(str, alice_final))}, Bob = {''.join(map(str, bob_final))}")
        print(f"    Raw Errors = {protocol.final_key_errors} bit error(s) | Match = {'100%' if summary['keys_match'] else 'Reconcile Required'}")
        print("\nSTAGE-BY-STAGE TRANSMISSION TABLE:")
        print(format_protocol_table(summary))

    # Save Session Visualizations (both generic and prefixed)
    generate_all_visualizations(protocol, summary, circuits_dir, prefix=prefix)

    # Export Reports
    export_results(summary, results_dir, prefix=prefix)

    return summary


def run_full_suite(
    num_qubits: int = 24,
    seed: int = 10,
    noise_prob: float = 0.12,
    sample_ratio: float = 0.25
):
    """
    Executes the comprehensive BB84 study across all noise configurations:
      1. Ideal Channel (p=0.0)
      2. Bit Flip X Noise (p)
      3. Phase Flip Z Noise (p)
      4. Bit and Phase Flip Y/XZ Noise (p)
      5. Amplitude Damping Noise (p)
      6. Depolarizing Noise (p)
    Generates multi-noise comparative analysis and parameter sweep curves.
    """
    circuits_dir = os.path.join(os.getcwd(), "circuits")
    results_dir = os.path.join(os.getcwd(), "results")

    noise_models_config = [
        ("Ideal Channel", 0.0, "none", "bb84_ideal"),
        ("Bit Flip (X)", noise_prob, "bit_flip", "bb84_bit_flip"),
        ("Phase Flip (Z)", noise_prob, "phase_flip", "bb84_phase_flip"),
        ("Bit & Phase Flip", noise_prob, "bit_phase_flip", "bb84_bit_phase_flip"),
        ("Amplitude Damping", noise_prob, "amplitude_damping", "bb84_amplitude_damping"),
        ("Depolarizing", noise_prob, "depolarizing", "bb84_depolarizing"),
    ]

    all_summaries: Dict[str, Dict[str, Any]] = {}

    print("\n" + "=" * 90)
    print("          BB84 QUANTUM KEY DISTRIBUTION: COMPREHENSIVE NOISE STUDY")
    print("                      Powered Strictly by Qiskit & Qiskit Aer")
    print("=" * 90)

    for label, prob, ntype, prefix in noise_models_config:
        summary = run_single_session(
            num_qubits=num_qubits,
            seed=seed,
            noise_prob=prob,
            noise_type=ntype,
            sample_ratio=sample_ratio,
            circuits_dir=circuits_dir,
            results_dir=results_dir,
            prefix=prefix,
            verbose=True
        )
        all_summaries[label] = summary

    # Export multi-noise comparative reports
    print("\n[+] Generating Multi-Noise Comparative Visualizations & Reports...")
    comp_json, comp_txt = export_multi_noise_comparison(all_summaries, results_dir)
    print(f"    -> Saved Comparison JSON : {comp_json}")
    print(f"    -> Saved Comparison TXT  : {comp_txt}")

    # Generate Multi-Noise Infographic
    comp_img = os.path.join(circuits_dir, "noise_models_comparison_analysis.png")
    save_all_noise_models_comparison_image(all_summaries, comp_img)
    print(f"    -> Saved Comparison Plot : {comp_img}")

    # Generate Dedicated Bit & Phase Flip vs Amplitude Damping Infographic
    bpf_ad_img = os.path.join(circuits_dir, "bit_phase_flip_and_amplitude_damping_analysis.png")
    save_bit_phase_flip_and_amplitude_damping_analysis(all_summaries, bpf_ad_img)
    print(f"    -> Saved BPF vs AD Plot  : {bpf_ad_img}")

    # Generate Multi-Noise Parameter Sweep (0% to 20%)
    sweep_img = os.path.join(circuits_dir, "all_noise_models_sweep.png")
    save_multi_noise_sweep_image(sweep_img, num_trials=6)
    print(f"    -> Saved Multi-Sweep Plot: {sweep_img}")

    # Also maintain default bb84 files for convenience
    export_results(all_summaries["Bit Flip (X)"], results_dir, prefix="bb84")

    # Print Final Comparative Summary Table
    print("\n" + "=" * 115)
    print(" " * 36 + "BB84 NOISE MODELS COMPARATIVE SUMMARY")
    print("=" * 115)
    print(format_multi_noise_comparison_table(all_summaries))
    print("=" * 115 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BB84 QKD Simulator: Multi-Noise Study with Qiskit")
    parser.add_argument("--qubits", type=int, default=24, help="Number of qubits to transmit (default: 24)")
    parser.add_argument("--seed", type=int, default=10, help="Random seed for reproducibility (default: 10)")
    parser.add_argument("--noise-prob", type=float, default=0.12, help="Noise error parameter (default: 0.12)")
    parser.add_argument("--sample-ratio", type=float, default=0.25, help="Sample ratio for QBER verification (default: 0.25)")
    parser.add_argument(
        "--noise-type",
        type=str,
        default="all",
        choices=["all", "none", "bit_flip", "phase_flip", "bit_phase_flip", "amplitude_damping", "depolarizing"],
        help="Noise model type to simulate (default: all)"
    )
    args = parser.parse_args()

    if args.noise_type == "all":
        run_full_suite(
            num_qubits=args.qubits,
            seed=args.seed,
            noise_prob=args.noise_prob,
            sample_ratio=args.sample_ratio
        )
    else:
        circuits_dir = os.path.join(os.getcwd(), "circuits")
        results_dir = os.path.join(os.getcwd(), "results")
        prefix = f"bb84_{args.noise_type}" if args.noise_type != "none" else "bb84_ideal"
        run_single_session(
            num_qubits=args.qubits,
            seed=args.seed,
            noise_prob=args.noise_prob if args.noise_type != "none" else 0.0,
            noise_type=args.noise_type,
            sample_ratio=args.sample_ratio,
            circuits_dir=circuits_dir,
            results_dir=results_dir,
            prefix=prefix,
            verbose=True
        )
