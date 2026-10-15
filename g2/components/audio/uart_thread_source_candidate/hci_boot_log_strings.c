#include <stdint.h>

/* Exact NUL-terminated stock HCI boot log templates. */
const uint8_t audio_ble_hci_boot_log_first[56]
    __attribute__((section(".g2_rom_0071f5d0"))) =
    "am_devices_em9305_init status:0x%x, need_force_dfu:%d\r\n";
const uint8_t audio_ble_hci_boot_log_retry[36]
    __attribute__((section(".g2_rom_00754ad0"))) =
    "em9305 reset error need force dfu\r\n";
