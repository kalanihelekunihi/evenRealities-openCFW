#!/usr/bin/env python3
"""Compile and check bounded C legacy advertising HCI transitions."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_adv_hci_4ba4b0.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj = directory / "adv-hci.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
        symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(obj)], text=True)
        assert "audio_ble_dm_adv_hci_handler_4ba4b0" in symbols and "audio_ble_dm_adv_table" in symbols
        harness = directory / "harness.c"
        harness.write_text("""
#include <stdint.h>
#include <string.h>
extern void audio_ble_dm_adv_hci_handler_4ba4b0(void *);
uint8_t audio_ble_dm_adv_control[36];
uint8_t audio_ble_dm_handler_state[64];
uint8_t audio_ble_dm_leg_adv_type_20074fb3;
void audio_ble_dm_adv_reset_4ba45c(void) {}
void audio_ble_dm_adv_msg_handler_4ba6ac(void *p) { (void)p; }
static unsigned start_count, stop_count, priv_count, callback_count, conn_count;
static uint32_t start_duration;
static uint8_t priv_event, priv_param, conn_status;
static void *callback_arg;
void WsfTimerStartMs(void *p, uint32_t ms) {
    if (p != audio_ble_dm_adv_control) __builtin_trap();
    ++start_count; start_duration = ms;
}
void WsfTimerStop(void *p) { if (p != audio_ble_dm_adv_control) __builtin_trap(); ++stop_count; }
void dmDevPassEvtToDevPriv(uint8_t event, uint8_t param, uint8_t a, uint8_t b) {
    if (a || b) __builtin_trap();
    ++priv_count; priv_event = event; priv_param = param;
}
void audio_ble_dm_adv_gen_conn_complete_4b310a(uint8_t handle, uint8_t status) {
    if (handle) __builtin_trap(); ++conn_count; conn_status = status;
}
static void callback(void *p) { ++callback_count; callback_arg = p; }
int main(void) {
    void (*fn)(void *) = callback;
    memcpy(audio_ble_dm_handler_state + 8, &fn, sizeof fn);
    for (unsigned state = 0; state < 8; ++state) for (unsigned status = 0; status < 2; ++status)
    for (unsigned leg = 0; leg <= 4; leg += 4) for (unsigned duration = 0; duration <= 10; duration += 10)
    for (unsigned event_code = 0x34; event_code <= 0x35; ++event_code) {
        uint8_t event[40] = {0}; event[2] = (uint8_t)event_code; event[3] = (uint8_t)status;
        memset(audio_ble_dm_adv_control, 0, sizeof audio_ble_dm_adv_control);
        audio_ble_dm_adv_control[0x18] = 0x77;
        audio_ble_dm_adv_control[0x1d] = (uint8_t)state;
        audio_ble_dm_adv_control[0x20] = (uint8_t)duration;
        audio_ble_dm_leg_adv_type_20074fb3 = (uint8_t)leg;
        start_count = stop_count = priv_count = callback_count = conn_count = 0;
        callback_arg = 0;
        audio_ble_dm_adv_hci_handler_4ba4b0(event);
        unsigned active = event_code == 0x35u;
        unsigned started = active && state >= 2u && state <= 3u && status == 0u;
        unsigned stopped = active && state >= 4u && state <= 5u && status == 0u;
        unsigned timer_start = started && state == 3u && duration != 0u;
        unsigned timer_stop = stopped && state == 5u;
        unsigned callback_expected = (started && state == 3u && leg != 4u) ||
                                     (stopped && state == 5u && leg != 4u);
        unsigned conn_expected = stopped && state == 5u && leg == 4u;
        unsigned final_state = state;
        if (active && state >= 2u && state <= 3u) final_state = status ? 0u : 1u;
        if (active && state >= 4u && state <= 5u) final_state = status ? 1u : 0u;
        unsigned final_type = started ? leg : (stopped ? 0xffu : 0x77u);
        unsigned final_event = callback_expected ? (started ? 0x21u : 0x22u) : event_code;
        if (audio_ble_dm_adv_control[0x18] != final_type ||
            audio_ble_dm_adv_control[0x1d] != final_state ||
            audio_ble_dm_adv_control[0x0a] != (timer_start ? 7u : 0u) ||
            event[2] != final_event || start_count != timer_start || stop_count != timer_stop ||
            priv_count != started + stopped || callback_count != callback_expected ||
            conn_count != conn_expected) return 1;
        if ((timer_start && start_duration != duration) ||
            (started && (priv_event != 12u || priv_param != 0x21u)) ||
            (stopped && (priv_event != 13u || priv_param != 0x22u)) ||
            (callback_expected && callback_arg != event) ||
            (conn_expected && conn_status != 0x3cu)) return 2;
    }
    return 0;
}
""")
        binary = directory / "harness"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(SOURCE), str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    print(json.dumps({"status": "PASS_BOUNDED_DM_ADV_HCI_C", "cases": 128,
                      "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
