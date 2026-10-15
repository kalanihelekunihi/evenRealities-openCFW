#!/usr/bin/env python3
"""Compile recovered CMSIS thread and adjacent audio lower C graph."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-ambiq-graph.o"
PRIOR = OUT / "ambiq-graph-current-receipt.json"
BOUND = OUT / "apollo-main-thread-audio-lowers.o"
RECEIPT = OUT / "thread-audio-lowers-current-receipt.json"
THREAD = "assert_failure dynamic_create initialize_stack initialize_tcb list_init schedule_tcb static_create thread_new".split()
AUDIO = {
    "scheduler_delay_candidate": ["delay"],
    "file_backend_close_candidate": ["backend_close"],
    "classify_adapter_candidate": ["alias"],
    "uart_irq_source_candidate": "delay_bridge fifo_bridge irq_service lower_dma read_abort read_sm rx_abort tx_bridge".split(),
}
ORACLES = {
    "verify_thread_new.py": "PASS_THREAD_NEW_BOUNDED 21",
    "verify_initialize_tcb.py": "PASS_INITIALIZE_TCB_BOUNDED 9",
    "verify_assert_failure.py": "PASS_ASSERT_FAILURE_PREFIX",
    "verify_initialize_stack.py": "PASS_INITIALIZE_STACK_FRAME 8",
    "verify_thread_list_init.py": "PASS_THREAD_LIST_INIT_BOUNDED 61",
    "verify_file_backend_close.py": "PASS_FILE_BACKEND_CLOSE_BOUNDED 20",
    "verify_classify_adapter.py": "PASS_CLASSIFY_ADAPTER 24",
    "verify_delay_bounded.py": "PASS_BOUNDED_DELAY 64",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, option):
    output = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3
            and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 583
    sources = [(G2 / "components/audio/thread_new_source_candidate" / (stem + ".c"),
                OUT / "thread-current" / (stem + ".o")) for stem in THREAD]
    sources += [(G2 / "components/audio" / folder / (stem + ".c"),
                 OUT / "audio-lower-current" / (stem + ".o"))
                for folder, stems in AUDIO.items() for stem in stems]
    assert len(sources) == 19 and len({obj.name for _, obj in sources}) == 19
    seen = defined(BASE)
    rows = []
    objects = []
    for source, obj in sources:
        obj.parent.mkdir(parents=True, exist_ok=True)
        flags = ["-Wno-unused-function"] if source.stem in {"fifo_bridge", "read_sm", "tx_bridge"} else []
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", *flags, "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        names = defined(obj)
        assert names and not names & seen, (source, names & seen)
        seen |= names
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                     "defined": sorted(names), "warning_exception": flags})
        objects.append(obj)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert defined(BOUND) == seen
    assert not after - before and len(before - after) == 10 and len(after) == 573
    oracles = []
    for name, expected in ORACLES.items():
        path = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True, check=True)
        assert result.stdout.strip().splitlines()[-1] == expected, (name, result.stdout)
        oracles.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                        "observed": expected})
    uart = G2 / "analysis/audio-source-candidate-20261010/verify_uart_irq_full_local.py"
    result = subprocess.run([sys.executable, str(uart)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1].startswith("PASS 704 joined local graph cases")
    oracles.append({"path": str(uart.relative_to(ROOT)), "sha256": sha(uart),
                    "observed": result.stdout.strip().splitlines()[-1]})
    receipt = {
        "status": "PASS_CURRENT_MAIN_THREAD_AUDIO_LOWERS_COMPILE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows, "source_unit_count": len(rows),
        "bounded_oracles_rerun": oracles,
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["UART IRQ comparison has explicit memset and delay cuts and synthetic registers",
                   "Thread scheduling, storage ownership, asynchronous timing, and physical UART behavior remain unqualified",
                   "Three UART wrappers suppress unused static declarations from included compatibility headers"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "units": len(rows),
                      "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
