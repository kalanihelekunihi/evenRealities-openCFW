/* Native Cordio AttcWriteCmd 0x539dea. */
#include <stdint.h>

extern void *audio_ble_att_message_allocate_4b50ae(uint16_t);
extern void *audio_ble_attc_send_message_4b5640(uint8_t, uint16_t, uint8_t,
                                                 void *, uint8_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

uint32_t audio_ble_attc_write_command_539dea(uint8_t connection,
                                              uint16_t handle,
                                              uint16_t length,
                                              const uint8_t *value)
{
    uint8_t *packet = (uint8_t *)audio_ble_att_message_allocate_4b50ae(
        (uint16_t)(length + 11u));
    if (packet == 0)
        return (uint32_t)(uintptr_t)value;
    uint16_t payload_length = (uint16_t)(length + 3u);
    packet[0] = (uint8_t)payload_length;
    packet[1] = (uint8_t)(payload_length >> 8);
    packet[8] = 0x52u;
    packet[9] = (uint8_t)handle;
    packet[10] = (uint8_t)(handle >> 8);
    (void)audio_queue_copy_bytes(packet + 11u, value, length);
    (void)audio_ble_attc_send_message_4b5640(connection, handle, 10u,
                                               packet, 0u);
    return 0u;
}
