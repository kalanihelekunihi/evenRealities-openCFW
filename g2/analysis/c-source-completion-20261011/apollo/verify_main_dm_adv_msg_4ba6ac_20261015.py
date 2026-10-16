#!/usr/bin/env python3
"""Check the bounded stock advertising dispatch evidence and C candidate."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_adv_msg_4ba6ac.c"
BASE = 0x438000
EXPECTED = [0x4b9ac1, 0x4b9d25, 0x4b9e89, 0x4ba0f5,
            0x4ba33d, 0x4ba33f, 0x4ba341, 0x4ba343]


def main():
    package = PAYLOAD.read_bytes()
    payload = package[32:]
    assert hashlib.sha256(payload).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    at = lambda address: address - BASE
    assert payload[at(0x4ba6ac):at(0x4ba6c0)].hex() == "80b5dff8e415827812f0070251f82210884701bd"
    actual = list(struct.unpack_from("<8I", payload, at(0x75f550)))
    assert actual == EXPECTED
    assert all(payload[at(address & ~1):at(address & ~1) + 2] == b"\x70\x47"
               for address in EXPECTED[4:7])
    with tempfile.TemporaryDirectory() as directory:
        obj = Path(directory) / "adv-msg.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", str(obj)], text=True)
        for name in ("audio_ble_dm_adv_msg_handler_4ba6ac",
                     "audio_ble_dm_adv_actions_75f550",
                     "audio_ble_dm_adv_remove_set_4ba33c",
                     "audio_ble_dm_adv_clear_sets_4ba33e",
                     "audio_ble_dm_adv_set_rand_addr_4ba340"):
            assert name in symbols
        for name in ("audio_ble_dm_adv_config_4b9ac0",
                     "audio_ble_dm_adv_set_data_4b9d24",
                     "audio_ble_dm_adv_start_4b9e88",
                     "audio_ble_dm_adv_stop_4ba0f4",
                     "audio_ble_dm_adv_timeout_4ba342"):
            assert name in symbols
        harness = Path(directory) / "harness.c"
        harness.write_text("""
#include <stdint.h>
extern void audio_ble_dm_adv_msg_handler_4ba6ac(void *);
static unsigned calls[8];
static void *last_message;
static unsigned config_calls;
static unsigned adv_data_calls;
static unsigned scan_data_calls;
static uint8_t config_type, config_peer_type, data_length;
static const uint8_t *config_address, *data_address;
uint8_t audio_ble_dm_adv_control[36];
static unsigned hci_calls;
static uint8_t last_enable;
void HciLeSetAdvEnableCmd(uint8_t enable) { last_enable = enable; ++hci_calls; }
void audio_ble_dm_adv_config_lower_4b9a80(uint8_t type, uint8_t peer_type, const uint8_t *address) {
    ++config_calls; config_type = type; config_peer_type = peer_type; config_address = address;
}
void HciLeSetAdvDataCmd(uint8_t length, const uint8_t *data) {
    ++adv_data_calls; data_length = length; data_address = data;
}
void HciLeSetScanRespDataCmd(uint8_t length, const uint8_t *data) {
    ++scan_data_calls; data_length = length; data_address = data;
}
int main(void) {
    uint8_t message[12] = {0};
    for (unsigned event = 0; event < 256; ++event) {
        message[2] = (uint8_t)event;
        last_message = 0;
        audio_ble_dm_adv_msg_handler_4ba6ac(message);
        if (last_message != 0 || calls[event & 7u] != 0) return 1;
    }
    for (unsigned state = 0; state < 8; ++state) for (unsigned type = 0; type < 8; ++type) {
        audio_ble_dm_adv_control[0x1d] = (uint8_t)state;
        audio_ble_dm_adv_control[0x18] = (uint8_t)type;
        audio_ble_dm_adv_control[0x20] = 0;
        audio_ble_dm_adv_control[0x21] = 0;
        message[2] = 2;
        message[8] = 0x34;
        message[9] = 0x12;
        hci_calls = 0;
        audio_ble_dm_adv_msg_handler_4ba6ac(message);
        unsigned start = state == 0u && type != 1u && type != 4u;
        if (hci_calls != start || audio_ble_dm_adv_control[0x1d] != (start ? 3u : state) ||
            audio_ble_dm_adv_control[0x20] != (start ? 0x34u : 0u) ||
            audio_ble_dm_adv_control[0x21] != (start ? 0x12u : 0u) ||
            (start && last_enable != 1u)) return 5;
        for (unsigned action = 3; action <= 7; action += 4) {
            audio_ble_dm_adv_control[0x1d] = (uint8_t)state;
            audio_ble_dm_adv_control[0x18] = (uint8_t)type;
            hci_calls = 0;
            message[2] = (uint8_t)action;
            audio_ble_dm_adv_msg_handler_4ba6ac(message);
            unsigned expected = state == 1u && (action == 7u || (type != 1u && type != 4u));
            if (hci_calls != expected || audio_ble_dm_adv_control[0x1d] != (expected ? 5u : state) ||
                (expected && last_enable != 0u)) return 4;
        }
    }
    for (unsigned state = 0; state < 8; ++state) for (unsigned type = 0; type < 8; ++type) {
        audio_ble_dm_adv_control[0x1d] = (uint8_t)state;
        audio_ble_dm_adv_control[0x18] = (uint8_t)type;
        message[2] = 0; message[5] = 2; message[6] = 3;
        unsigned before = config_calls;
        audio_ble_dm_adv_msg_handler_4ba6ac(message);
        unsigned expected = state == 0u && type != 1u && type != 4u;
        if (config_calls != before + expected || (expected && (config_type != 2u ||
            config_peer_type != 3u || config_address != message + 7))) return 6;
    }
    for (unsigned state = 0; state < 8; ++state) for (unsigned location = 0; location < 3; ++location) {
        audio_ble_dm_adv_control[0x1d] = (uint8_t)state;
        message[2] = 1; message[6] = (uint8_t)location; message[7] = 4;
        unsigned before_adv = adv_data_calls, before_scan = scan_data_calls;
        audio_ble_dm_adv_msg_handler_4ba6ac(message);
        unsigned expected = state == 0u;
        if (adv_data_calls != before_adv + (expected && location == 0u) ||
            scan_data_calls != before_scan + (expected && location != 0u) ||
            (expected && (data_length != 4u || data_address != message + 8))) return 7;
    }
    return 0;
}
""")
        binary = Path(directory) / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_ADV_MSG_C",
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                      "stock_action_pointers": [hex(address) for address in actual],
                      "event_byte_cases": 256, "action_state_cases": 280,
                      "boundaries": "Compiled all eight advertising actions and dispatcher against bounded state cases and exact stock table/dispatch/no-op bytes; native action oracle and integration are separate gates."}, indent=2))


if __name__ == "__main__":
    main()
