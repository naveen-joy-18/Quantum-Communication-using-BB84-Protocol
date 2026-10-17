"""
src/utils.py
Helper functions for formatting, reporting, and exporting BB84 protocol data.
Supports both Ideal and Noisy Channel configurations.
"""

import os
import json
from typing import Dict, Any


def ensure_dir(dir_path: str):
    """Ensures that a directory exists."""
    os.makedirs(dir_path, exist_ok=True)


def format_protocol_table(summary: Dict[str, Any]) -> str:
    """
    Creates an aligned table displaying the stage-by-stage BB84 execution
    for every transmitted qubit, highlighting noisy bit-flips when bases matched.
    """
    n = summary["total_qubits_sent"]
    alice_bits = summary["alice_bits"]
    alice_bases = summary["alice_bases"]
    alice_states = summary["alice_states"]
    bob_bases = summary["bob_bases"]
    bob_results = summary["bob_results"]
    matches = summary["matching_basis_mask"]

    lines = []
    header = (
        f"{'Qubit':^7}|{'Alice Bit':^11}|{'Alice Basis':^13}|{'State':^9}|"
        f"{'Bob Basis':^11}|{'Bob Result':^12}|{'Basis Match?':^14}|{'Sifted Result':^15}"
    )
    separator = "-" * len(header)
    lines.append(separator)
    lines.append(header)
    lines.append(separator)

    for i in range(n):
        if matches[i]:
            if alice_bits[i] == bob_results[i]:
                match_str = "MATCH (OK)"
                sifted_val = f"{alice_bits[i]} (Valid)"
            else:
                match_str = "ERROR (NOISE)"
                sifted_val = f"A:{alice_bits[i]}!=B:{bob_results[i]}"
        else:
            match_str = "MISMATCH"
            sifted_val = "-- (Discard)"

        row = (
            f"{i:^7}|{alice_bits[i]:^11}|{alice_bases[i]:^13}|{alice_states[i]:^9}|"
            f"{bob_bases[i]:^11}|{bob_results[i]:^12}|{match_str:^14}|{sifted_val:^15}"
        )
        lines.append(row)

    lines.append(separator)
    return "\n".join(lines)


def generate_text_report(summary: Dict[str, Any]) -> str:
    """
    Generates a full textual report with metrics and key details.
    """
    is_noisy = summary.get("is_noisy", False)
    channel_desc = (
        f"Noisy Channel ({summary.get('noise_type', 'depolarizing').title()} Noise, p = {summary.get('noise_prob', 0.0)})"
        if is_noisy else "Normal / Ideal (Noise-Free, No Eavesdropper)"
    )

    report = []
    report.append("=" * 80)
    report.append(" " * 22 + "BB84 QUANTUM KEY DISTRIBUTION REPORT")
    report.append("=" * 80)
    report.append(f"Simulation Engine           : Qiskit AerSimulator (Quantum Simulation)")
    report.append(f"Protocol Specification      : BB84 (Charles Bennett & Gilles Brassard, 1984)")
    report.append(f"Quantum Channel State       : {channel_desc}")
    report.append("-" * 80)
    report.append("KEY METRICS & PERFORMANCE:")
    report.append(f"  • Total Qubits Transmitted: {summary['total_qubits_sent']}")
    report.append(f"  • Sifted Key Length       : {summary['sifted_key_length']} bits")
    report.append(f"  • Sifting Efficiency     : {summary['sifting_efficiency_percent']}% (Theoretical Expectation: ~50%)")
    report.append(f"  • Sample Verification Size: {summary['sample_verification_size']} bits")
    report.append(f"  • Sample QBER             : {summary['qber_percent']}%")
    report.append(f"  • Total Sifted Key QBER   : {summary.get('total_sifted_qber_percent', summary['qber_percent'])}%")
    report.append(f"  • BB84 Security Threshold : {summary.get('bb84_threshold_percent', 11.0)}% (Shor-Preskill Bound)")
    report.append(f"  • Channel Security Status : {summary.get('security_status', 'N/A')}")
    report.append(f"  • Final Key Length        : {summary['final_key_length']} bits")
    report.append(f"  • Raw Final Key Errors    : {summary.get('final_key_errors', 0)} bit errors")
    report.append(f"  • Raw Keys Identical      : {'YES (100% Match)' if summary['keys_match'] else 'NO (Channel noise introduced bit flips)'}")
    report.append("-" * 80)
    report.append("SHARED FINAL SECRET KEYS:")
    report.append(f"  Alice's Key : {summary['alice_final_key']}")
    report.append(f"  Bob's Key   : {summary['bob_final_key']}")
    report.append("=" * 80)
    report.append("\nBIT-BY-BIT TRANSMISSION DETAILS:\n")
    report.append(format_protocol_table(summary))
    report.append("\n" + "=" * 80)
    return "\n".join(report)


def export_results(summary: Dict[str, Any], output_dir: str, prefix: str = "bb84"):
    """
    Saves JSON and TXT report to the results directory with a specified prefix.
    """
    ensure_dir(output_dir)
    json_path = os.path.join(output_dir, f"{prefix}_run_summary.json")
    txt_path = os.path.join(output_dir, f"{prefix}_detailed_report.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(generate_text_report(summary))

    return json_path, txt_path


def format_multi_noise_comparison_table(all_summaries: Dict[str, Dict[str, Any]]) -> str:
    """
    Creates an aligned comparative table across all noise models.
    """
    col_width = 18
    headers = ["Metric"] + [name for name in all_summaries.keys()]
    header_str = f"{headers[0]:<28} | " + " | ".join(f"{h:^{col_width}}" for h in headers[1:])
    separator = "-" * len(header_str)

    lines = [separator, header_str, separator]

    metrics_rows = [
        ("Noise Probability (p)", lambda s: f"{s.get('noise_prob', 0.0):.2f}"),
        ("Transmitted Qubits", lambda s: f"{s['total_qubits_sent']}"),
        ("Sifted Key Length", lambda s: f"{s['sifted_key_length']} bits"),
        ("Sifting Efficiency", lambda s: f"{s['sifting_efficiency_percent']}%"),
        ("Sample QBER", lambda s: f"{s['qber_percent']}%"),
        ("Total Sifted QBER", lambda s: f"{s.get('total_sifted_qber_percent', s['qber_percent'])}%"),
        ("Z-Basis QBER", lambda s: f"{s.get('z_basis_qber_percent', 0.0)}%"),
        ("X-Basis QBER", lambda s: f"{s.get('x_basis_qber_percent', 0.0)}%"),
        ("Threshold (11.0%)", lambda s: "PASSED" if s.get('total_sifted_qber_percent', s['qber_percent']) <= 11.0 else "EXCEEDED"),
        ("Final Key Length", lambda s: f"{s['final_key_length']} bits"),
        ("Raw Key Errors", lambda s: f"{s.get('final_key_errors', 0)}"),
        ("Key Integrity", lambda s: "MATCH (100%)" if s['keys_match'] else "RECONCILE"),
    ]

    for label, extractor in metrics_rows:
        row_vals = [extractor(all_summaries[k]) for k in all_summaries.keys()]
        row_str = f"{label:<28} | " + " | ".join(f"{v:^{col_width}}" for v in row_vals)
        lines.append(row_str)

    lines.append(separator)
    return "\n".join(lines)


def export_multi_noise_comparison(all_summaries: Dict[str, Dict[str, Any]], output_dir: str):
    """
    Exports comprehensive JSON and TXT comparison reports across all noise models.
    """
    ensure_dir(output_dir)
    json_path = os.path.join(output_dir, "bb84_all_noise_models_comparison.json")
    txt_path = os.path.join(output_dir, "bb84_all_noise_models_comparison.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=4)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 115 + "\n")
        f.write(" " * 32 + "BB84 NOISE MODELS COMPARATIVE REPORT\n")
        f.write("=" * 115 + "\n\n")
        f.write(format_multi_noise_comparison_table(all_summaries))
        f.write("\n\n" + "=" * 115 + "\n")

    return json_path, txt_path

