/* EM9305 vendor-specific BD address update, AmbiqSuite Cordio EM9305 HCI
 * driver (no log strings; stock path unknown). Native HciVscUpdateBDAddress
 * 0x4b4d08..0x4b4d17, literal 0x4b4d98 -> RAM 0x20074148.
 *
 * Stock variant of AmbiqSuite R3.2.0 hci_drv_apollo3.c HciVscUpdateBDAddress,
 * which sends Apollo3 opcode 0xFC32; the EM9305 build sends
 * EMSG_OPCODE_SET_PUBLIC_ADDRESS 0xFC43 (alias 0xFC02) with the 6-byte
 * g_BLEMacAddress. Called from hciCoreResetStart 0x569b4a right after
 * HCI_Reset. */
#include <stdint.h>

#define EM9305_VSC_SET_PUBLIC_ADDRESS 0xfc43u

extern uint8_t audio_ble_custom_bd_address[6]; /* g_BLEMacAddress, RAM 0x20074148 */
extern void audio_ble_hci_vendor_specific_cmd(uint16_t opcode, uint8_t length,
                                              const void *payload); /* HciVendorSpecificCmd 0x52b84c */

void HciVscUpdateBDAddress(void);

void HciVscUpdateBDAddress(void)
{
    audio_ble_hci_vendor_specific_cmd(EM9305_VSC_SET_PUBLIC_ADDRESS, 6u, audio_ble_custom_bd_address);
}
