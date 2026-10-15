#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern void audio_ble_slave_finish_4b3944(const void *, void *);
extern void audio_ble_slave_finish_4b39de(const void *, void *);
extern void audio_ble_slave_finish_4b3aa8(const void *, void *);
extern void audio_ble_slave_finish_4b3aea(const void *, void *);
extern void audio_ble_slave_finish_4b3aec(const void *, void *);
extern void audio_ble_slave_finish_4b3a86(const void *, void *);
extern void audio_ble_slave_finish_4b3b4c(const void *, void *);
extern void audio_ble_slave_finish_4b39f6(const void *, void *);
extern void audio_ble_slave_finish_4b3bb4(const void *, void *);
extern void audio_ble_slave_finish_4b3bd2(const void *, void *);
extern void audio_ble_slave_finish_4b3ba0(const void *, void *);

/* Native AppSlaveProcDmMsg 0x4b45b0 second-stage event switch. */
void audio_ble_comm_slave_finish(void *message)
{
    const uint8_t *bytes = (const uint8_t *)message;
    uint16_t connection = (uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8);
    uint8_t event = bytes[2];
    void *row = 0;
    if (event != 0x3fu && connection != 0u && connection < 4u)
        row = audio_ble_discovery_connection_records_200717b0 +
              ((uint32_t)connection - 1u) * 0x30u;
    switch (event) {
    case 0x27u: if (row) audio_ble_slave_finish_4b3944(message, row); break;
    case 0x28u: if (row) audio_ble_slave_finish_4b39de(message, row); break;
    case 0x2au: if (row) audio_ble_slave_finish_4b3aa8(message, row); break;
    case 0x2bu: if (row) audio_ble_slave_finish_4b3aea(message, row); break;
    case 0x2cu: if (row) audio_ble_slave_finish_4b3aec(message, row); break;
    case 0x2fu: if (row) audio_ble_slave_finish_4b3a86(message, row); break;
    case 0x30u: if (row) audio_ble_slave_finish_4b3b4c(message, row); break;
    case 0x31u: if (row) audio_ble_slave_finish_4b39f6(message, row); break;
    case 0x3au: if (row) audio_ble_slave_finish_4b3bb4(message, row); break;
    case 0x3bu: if (row) audio_ble_slave_finish_4b3bd2(message, row); break;
    case 0x3fu: audio_ble_slave_finish_4b3ba0(message, row); break;
    default: break;
    }
}
