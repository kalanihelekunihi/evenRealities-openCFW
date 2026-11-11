/* HciDrvRadioBoot 0x4b48a6 is an alias of audio_ble_hci_driver_radio_boot
 * in ble/ble-hci/display_ble_hci_radio_boot.c (formerly a forwarding wrapper here). */
#include <stdint.h>

/* Native DmDevVsInit 0x4b308c..0x4b3096: the product build has no vendor HCI
 * init, so the stock body only narrows its argument and returns. Its IAR
 * epilogue popped the caller's R7 into R0; the function and its only caller
 * (display_ble_stack_init.c) are void. */
void DmDevVsInit(uint32_t handler) {
    (void)handler;
}
