/* Live Apollo BLE callback cells at 0x200740fc and 0x20074100.
 * Boot initialization of these cells is not established by their addresses. */
#include <stdint.h>

uint32_t (*audio_ble_subsystem_primary_callback_slot)(const uint8_t *)
    __attribute__((section(".bss.g2.ram.ble_subsystem_primary_callback_slot")));
uint32_t (*audio_ble_subsystem_callback_slot)(const uint8_t *)
    __attribute__((section(".bss.g2.ram.ble_subsystem_callback_slot")));
