/* Native Apollo radio GPIO callback 0x4b4a98..0x4b4ab2.
 * This source joins the foundation radio_gpio C reduction to the Main
 * scheduler provider that reconstructs WsfSetEvent 0x52b91e. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_ble_hci_driver_handler_id[] __asm__("audio_ble_hci_driver_handler_id");
extern unsigned char g2ref_audio_ble_hci_radio_command_cell[] __asm__("audio_ble_hci_radio_command_cell");

extern uint32_t audio_ble_wsf_set_event(uint32_t handler, uint32_t mask);

/* Stock 0x4B4A98 (HciDrvIntService) */
void opencfw_radio_gpio_callback(void *argument) {
    (void)argument;
    volatile uint32_t *const counter = (volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_ble_hci_radio_command_cell);
    *counter = *counter + 1u;
    uint32_t handler = *(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_ble_hci_driver_handler_id);
    (void)audio_ble_wsf_set_event(handler, 1u);
}
