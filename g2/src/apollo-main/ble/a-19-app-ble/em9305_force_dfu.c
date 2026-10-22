/* EM9305 forced-DFU reboot, native 0x4b4888..0x4b48a5 (literal pool
 * 0x4b4d68..0x4b4d6f), placed directly before HciDrvRadioBoot 0x4b48a6 in the
 * Ambiq Cordio HCI driver object. Only caller is 0x581552.
 *
 * Setting the boot-retry byte (RAM 0x20074fcc) makes HciDrvRadioBoot rerun its
 * controller recover/reconfigure (image download) sequence even when the
 * EM9305 firmware revision matches; it is cleared again afterwards. */
#include <stdint.h>

extern volatile uint8_t audio_ble_hci_radio_boot_retry;               /* RAM 0x20074fcc */
extern void audio_ble_hci_boot_log_4733ee(const char *format, ...);    /* am_util_stdio_printf */
extern void HciDrvRadioBoot(uint8_t cold_boot);                        /* 0x4b48a6 */

static const char s_force_dfu[] = "SVC_BleEm9305ForceDfu\r\n"; /* ROM 0x77799c */

void svc_ble_em9305_force_dfu_4b4888(void)
{
    audio_ble_hci_boot_log_4733ee(s_force_dfu);
    audio_ble_hci_radio_boot_retry = 1u;
    HciDrvRadioBoot(0u);
    audio_ble_hci_radio_boot_retry = 0u;
}
