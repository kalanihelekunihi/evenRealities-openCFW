#!/usr/bin/env python3
"""Compile and compare bounded C advertising configuration behavior."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_adv_config_lower_4b9a80.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj = directory / "adv-config.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(obj)], text=True)
        for name in ("audio_ble_dm_adv_config_lower_4b9a80", "audio_ble_dm_ll_addr_type_4d2a84",
                     "HciLeSetAdvParamCmd", "audio_ble_dm_leg_adv_type_20074fb3"):
            assert name in symbols
        harness = directory / "harness.c"
        harness.write_text("""
#include <stdint.h>
#include <string.h>
extern void audio_ble_dm_adv_config_lower_4b9a80(uint8_t, uint8_t, const uint8_t *);
extern void HciLeSetAdvParamCmd(uint16_t, uint16_t, uint8_t, uint8_t, uint8_t,
                                const uint8_t *, uint8_t, uint8_t);
extern uint8_t audio_ble_dm_leg_adv_type_20074fb3;
uint8_t audio_ble_dm_adv_control[36];
uint8_t audio_ble_dm_handler_state[64];
static uint8_t command[40];
static uint16_t opcode, size;
static unsigned allocation, sent;
void *audio_ble_hci_cmd_alloc_52ae38(uint16_t op, uint16_t len) {
    opcode = op; size = len; memset(command, 0xa5, sizeof command);
    return allocation ? command : 0;
}
void audio_ble_hci_cmd_send(void *p) { if (p != command) __builtin_trap(); ++sent; }
static int payload(const uint8_t *address, uint8_t own_type) {
    const uint8_t expected[] = {0x40,0x06,0x80,0x07,4,own_type,1,
                                address ? 0x11 : 0,address ? 0x22 : 0,
                                address ? 0x33 : 0,address ? 0x44 : 0,
                                address ? 0x55 : 0,address ? 0x66 : 0,5,6};
    return opcode == 0x2006u && size == 15u &&
           memcmp(command + 3, expected, sizeof expected) == 0;
}
int main(void) {
    const uint8_t address[6] = {0x11,0x22,0x33,0x44,0x55,0x66};
    audio_ble_dm_adv_control[0x10] = 0x40; audio_ble_dm_adv_control[0x11] = 6;
    audio_ble_dm_adv_control[0x14] = 0x80; audio_ble_dm_adv_control[0x15] = 7;
    audio_ble_dm_adv_control[0x1a] = 5; audio_ble_dm_handler_state[0x11] = 6;
    allocation = 1;
    for (unsigned own = 0; own < 4; ++own) for (unsigned privacy = 0; privacy < 2; ++privacy)
    for (unsigned with_address = 0; with_address < 2; ++with_address) {
        const uint8_t *peer = with_address ? address : 0;
        audio_ble_dm_handler_state[0x0e] = (uint8_t)own;
        audio_ble_dm_handler_state[0x16] = (uint8_t)privacy;
        sent = 0;
        audio_ble_dm_adv_config_lower_4b9a80(4, 1, peer);
        uint8_t expected_own = (uint8_t)(privacy && own <= 1u ? own + 2u : own);
        if (sent != 1u || !payload(peer, expected_own) ||
            audio_ble_dm_leg_adv_type_20074fb3 != 4u) return 1;
    }
    for (unsigned with_address = 0; with_address < 2; ++with_address)
    for (allocation = 0; allocation < 2; ++allocation) {
        const uint8_t *peer = with_address ? address : 0;
        sent = 0;
        HciLeSetAdvParamCmd(0x640, 0x780, 4, 2, 1, peer, 5, 6);
        if (opcode != 0x2006u || size != 15u || sent != allocation ||
            (allocation && !payload(peer, 2))) return 2;
    }
    return 0;
}
""")
        binary = directory / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_DM_ADV_CONFIG_C", "cases": 20,
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
