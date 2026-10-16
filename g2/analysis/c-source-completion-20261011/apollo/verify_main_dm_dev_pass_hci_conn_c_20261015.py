#!/usr/bin/env python3
"""Compile and check dynamic DM connection callback forwarding in C."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_dev_pass_hci_conn_4d29c2.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj = directory / "pass-hci-conn.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(obj)], text=True)
        assert "audio_ble_dm_dev_pass_hci_conn_4d29c2" in symbols
        harness = directory / "harness.c"
        harness.write_text("""
#include <stdint.h>
#include <string.h>
extern void audio_ble_dm_dev_pass_hci_conn_4d29c2(void *);
uint8_t audio_ble_dm_config[64];
static unsigned calls;
static void *last;
static void wrong(void *p) { (void)p; __builtin_trap(); }
static void right(void *p) { ++calls; last = p; }
int main(void) {
    void (*table[2])(void *) = {wrong, right};
    uintptr_t owner = (uintptr_t)table;
    for (unsigned i = 0; i < sizeof owner; ++i)
        audio_ble_dm_config[0x0c + i] = (uint8_t)(owner >> (8u * i));
    for (unsigned seed = 0; seed < 16; ++seed) {
        uint8_t event[36];
        for (unsigned i = 0; i < 36; ++i) event[i] = (uint8_t)(seed + i);
        last = 0; unsigned before = calls;
        audio_ble_dm_dev_pass_hci_conn_4d29c2(event);
        if (calls != before + 1u || last != event) return 1;
    }
    return 0;
}
""")
        binary = directory / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_DM_DEV_PASS_HCI_CONN_C", "cases": 16,
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
