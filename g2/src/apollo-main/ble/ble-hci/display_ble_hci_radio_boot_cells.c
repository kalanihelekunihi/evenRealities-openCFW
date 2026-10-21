/* Bounded HCI radio boot cells from native Main 0x4b48a6. The five
 * consecutive 32-bit control words start at 0x20074630; retry is one byte
 * at 0x20074fcc and revision is one word at 0x20074954. Full SRAM layout,
 * scheduler buffers, and ROM tables remain separate image obligations. */
#include <stdint.h>

volatile uint32_t audio_ble_hci_radio_context_ptr __attribute__((section(".g2_ram_20074630")));
volatile uint32_t audio_ble_hci_radio_aux_ptr __attribute__((section(".g2_ram_20074634")));
volatile uint32_t audio_ble_hci_radio_active __attribute__((section(".g2_ram_20074638")));
volatile uint32_t audio_ble_hci_radio_pending __attribute__((section(".g2_ram_2007463c")));
volatile uint32_t audio_ble_hci_radio_command_cell __attribute__((section(".g2_ram_20074640")));
volatile uint32_t audio_ble_hci_radio_revision_cell __attribute__((section(".g2_ram_20074954")));
volatile uint8_t audio_ble_hci_radio_boot_retry __attribute__((section(".g2_ram_20074fcc")));
