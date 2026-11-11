/* Observed direct BLE controller RAM slice through handler byte +0x56. */
#include <stdint.h>

uint8_t audio_ble_controller[0x57u]
    __attribute__((section(".g2_ram_200727f0")));
/* Stock 0x200727f0 is a single cell: one literal-pool word 0x4b81fc is loaded by
 * bleDmCback 0x4b74e0, bleProcMsg 0x4b7c8e and bleCommHandlerInit 0x4b7e78 (handler +0x56).
 * Alias so the comm-state and controller users share it (Fix 33). */
extern uint8_t audio_ble_comm_state[0x57u] __attribute__((alias("audio_ble_controller")));
