/* UX_SendBLEStatusToPeer, module g2-ux-system, firmware 2.2.6.10.
 * Stock range 0x47ce90..0x47ced5 (literal pool entries 0x47d8fc, 0x47d900).
 *
 * Sends the 8-byte BLE status packet (template ROM 0x78eddc, command 3) to the
 * peer on app id 0x103: byte 4 = device role, byte 5 = 2 on the master (role
 * 1) else 1, byte 6 = bit 2 of the packed UX status byte (RAM 0x20075043). */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);                 /* 0x45a568 */
extern uint32_t audio_uart_request_send(uint32_t app, const void *bytes, uint32_t length,
                                        uint32_t id);            /* 0x4651e0 SendDataToPeer */
extern volatile uint8_t audio_ota_packed_status;                 /* RAM 0x20075043 */

static const uint8_t ble_status_template[8] = {3u, 0u, 1u, 0u, 0u, 0u, 0u, 0u}; /* ROM 0x78eddc */

/* Stock 0x0047CE90 (UX_SendBLEStatusToPeer) */
void UX_SendBLEStatusToPeer(void)
{
    uint8_t packet[8];
    uint32_t i;

    for (i = 0u; i < 8u; i++)
        packet[i] = ble_status_template[i];
    packet[4] = audio_uart_device_role_get();
    packet[5] = (audio_uart_device_role_get() == 1u) ? 2u : 1u;
    packet[6] = (uint8_t)((audio_ota_packed_status >> 2) & 1u);
    (void)audio_uart_request_send(0x103u, packet, 8u, 0u);
}
