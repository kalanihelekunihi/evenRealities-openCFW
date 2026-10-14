/* Bounded HCI radio boot cells from native Main 0x4b48a6. The five
 * consecutive 32-bit control words start at 0x20074630; retry is one byte
 * at 0x20074fcc and revision is one word at 0x20074954. Full SRAM layout,
 * scheduler buffers, and ROM tables remain separate image obligations. */
#include <stdint.h>

volatile uint32_t audio_ble_hci_radio_context_ptr;
volatile uint32_t audio_ble_hci_radio_aux_ptr;
volatile uint32_t audio_ble_hci_radio_active;
volatile uint32_t audio_ble_hci_radio_pending;
volatile uint32_t audio_ble_hci_radio_command_cell;
volatile uint32_t audio_ble_hci_radio_revision_cell;
volatile uint8_t audio_ble_hci_radio_boot_retry;
