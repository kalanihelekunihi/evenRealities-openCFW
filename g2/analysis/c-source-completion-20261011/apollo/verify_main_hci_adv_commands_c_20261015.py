#!/usr/bin/env python3
"""Compile and check the C legacy advertising HCI command payloads."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_adv_commands_52b3b0.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj = directory / "adv-hci.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(obj)], text=True)
        for name in ("HciLeSetAdvEnableCmd", "HciLeSetAdvDataCmd", "HciLeSetScanRespDataCmd"):
            assert name in symbols
        harness = directory / "harness.c"
        harness.write_text("""
#include <stdint.h>
#include <string.h>
extern void HciLeSetAdvEnableCmd(uint8_t);
extern void HciLeSetAdvDataCmd(uint8_t, const uint8_t *);
extern void HciLeSetScanRespDataCmd(uint8_t, const uint8_t *);
static uint8_t command[40], data[32];
static uint16_t opcode, size;
static unsigned sent, allocation;
void *audio_ble_hci_cmd_alloc_52ae38(uint16_t op, uint16_t len) {
    opcode = op; size = len; memset(command, 0xa5, sizeof command);
    return allocation ? command : 0;
}
void audio_ble_hci_cmd_send(void *p) { if (p != command) __builtin_trap(); ++sent; }
int main(void) {
    for (unsigned i = 0; i < 32; ++i) data[i] = (uint8_t)(i + 1u);
    for (unsigned enable = 0; enable < 3; ++enable) for (allocation = 0; allocation < 2; ++allocation) {
        sent = 0; HciLeSetAdvEnableCmd((uint8_t)(enable == 2u ? 255u : enable));
        if (opcode != 0x200au || size != 1u || sent != allocation) return 1;
        if (allocation && command[3] != (enable == 2u ? 255u : enable)) return 2;
    }
    const unsigned lengths[] = {0, 1, 8, 31};
    for (unsigned location = 0; location < 2; ++location) for (unsigned j = 0; j < 4; ++j)
    for (allocation = 0; allocation < 2; ++allocation) {
        unsigned length = lengths[j]; sent = 0;
        if (location == 0) HciLeSetAdvDataCmd((uint8_t)length, data);
        else HciLeSetScanRespDataCmd((uint8_t)length, data);
        if (opcode != (location == 0 ? 0x2008u : 0x2009u) || size != 32u || sent != allocation) return 3;
        if (allocation) {
            if (command[3] != length) return 4;
            for (unsigned k = 0; k < 31; ++k) if (command[4 + k] != (k < length ? data[k] : 0)) return 5;
        }
    }
    return 0;
}
""")
        binary = directory / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_HCI_ADV_COMMANDS_C", "cases": 22,
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      "limits": ["Lengths above 31 are guarded in C and outside the native oracle."]}, indent=2))


if __name__ == "__main__":
    main()
