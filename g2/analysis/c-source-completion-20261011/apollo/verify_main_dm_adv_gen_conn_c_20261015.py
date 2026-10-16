#!/usr/bin/env python3
"""Compile and check C synthetic enhanced connection-completion records."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_adv_gen_conn_4b310a.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj = directory / "adv-gen-conn.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(obj)], text=True)
        assert "audio_ble_dm_adv_gen_conn_complete_4b310a" in symbols
        harness = directory / "harness.c"
        harness.write_text("""
#include <stdint.h>
#include <string.h>
extern void audio_ble_dm_adv_gen_conn_complete_4b310a(uint8_t, uint8_t);
uint8_t audio_ble_dm_adv_control[0x34];
static uint8_t record[36];
static unsigned calls;
void audio_ble_dm_dev_pass_hci_conn_4d29c2(void *event) {
    ++calls; memcpy(record, event, sizeof record);
}
int main(void) {
    for (unsigned i = 0; i < 12; ++i) audio_ble_dm_adv_control[0x25 + i] = (uint8_t)(0x11 + i);
    audio_ble_dm_adv_control[0x31] = 1; audio_ble_dm_adv_control[0x32] = 2;
    const uint8_t statuses[] = {0, 1, 0x3c, 0xff};
    for (unsigned handle = 0; handle < 2; ++handle) for (unsigned i = 0; i < 4; ++i) {
        uint8_t expected[36] = {0};
        uint8_t status = statuses[i]; calls = 0;
        expected[2] = 2; expected[3] = expected[4] = status;
        expected[8] = 1; expected[9] = (uint8_t)(handle + 1);
        for (unsigned j = 0; j < 6; ++j) expected[10 + j] = (uint8_t)(0x11 + 6 * handle + j);
        audio_ble_dm_adv_gen_conn_complete_4b310a((uint8_t)handle, status);
        if (calls != 1 || memcmp(record, expected, sizeof record)) return 1;
    }
    return 0;
}
""")
        binary = directory / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_DM_ADV_GEN_CONN_C", "cases": 8,
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
