#!/usr/bin/env python3
"""Bound which 704 joined UART fixture cases apply to selected C sources."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
ANALYSIS = G2 / "analysis/audio-source-candidate-20261010"
COMPONENT = G2 / "components/audio/uart_irq_source_candidate"
RESULT = ANALYSIS / "uart-irq-full-local-results.json"
BUILD_RECEIPT = G2 / "build/c-firmware/20261014/main-root-dependencies/pool-state-uart-irq-experimental-receipt.json"
RECEIPT = G2 / "build/c-firmware/20261014/main-root-dependencies/uart-irq-oracle-transfer-receipt.json"
SAME = {"irq_service": "uart_irq_local_candidate",
        "lower_dma": "uart_irq_lower_candidate",
        "rx_abort": "uart_irq_rx_abort_candidate",
        "read_abort": "uart_irq_read_abort_candidate"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads(RESULT.read_text())
    build = json.loads(BUILD_RECEIPT.read_text())
    assert result["status"] == "PASS_LOCAL_GRAPH_WITH_MEMSET_DELAY_CUTS"
    assert result["cases"] == sum(result["groups"].values()) == 704
    assert build["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_UART_IRQ_C_GRAPH"
    source_matches = {}
    for component, analysis in SAME.items():
        selected = COMPONENT / f"{component}.c"
        fixture = ANALYSIS / f"{analysis}.c"
        assert selected.read_bytes() == fixture.read_bytes()
        assert build["source_sha256"][str(selected.relative_to(ROOT))] == sha(selected)
        assert result["source_sha256"][str(fixture)] == sha(fixture)
        source_matches[component] = sha(selected)
    selected = COMPONENT / "read_sm.c"
    fixture = ANALYSIS / "uart_irq_read_sm_candidate.c"
    normalized = fixture.read_text().replace(
        '#include "../../components/audio/uart_tx_offline/compat.h"',
        '#include "../uart_tx_offline/compat.h"')
    assert selected.read_text() == normalized
    assert build["source_sha256"][str(selected.relative_to(ROOT))] == sha(selected)
    source_matches["read_sm_normalized_include"] = sha(selected)
    receipt = {
        "status": "PASS_BOUNDED_UART_IRQ_ORACLE_SOURCE_TRANSFER",
        "joined_oracle_result": str(RESULT.relative_to(ROOT)),
        "joined_oracle_result_sha256": sha(RESULT),
        "pool_graph_receipt": str(BUILD_RECEIPT.relative_to(ROOT)),
        "pool_graph_receipt_sha256": sha(BUILD_RECEIPT),
        "cases": 704,
        "groups": result["groups"],
        "identical_or_include_normalized_source_sha256": source_matches,
        "whole_graph_native_equivalence": False,
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["The joined oracle uses fixture FIFO/TX bridges, queue source and delay stub; pooled bridge objects are not directly replayed here.",
                  "Stock memset and baud delay remain explicit boundaries in the 704 cases.",
                  "Asynchronous interrupt delivery, physical UART and final image placement remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["cases"], sha(RECEIPT))


if __name__ == "__main__":
    main()
