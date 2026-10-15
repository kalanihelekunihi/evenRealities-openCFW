#include <stdint.h>

/* Native RAM pointer cell 0x20074358. */
extern const uint8_t *audio_ble_comm_profile_slot;
extern uint8_t audio_ble_dm_sec_level_4b71b2(uint8_t);
extern void audio_ble_master_row_dispatch_503498(uint32_t, uint32_t, void *);

static uint8_t connection_of(const uint8_t *message)
{
    return message[0]; /* native loads the halfword, then truncates to byte */
}

/* Native 0x5037ea. Four separate state writes precede the dispatch. */
void audio_ble_master_event_5037ea(const void *message, void *record)
{
    volatile uint8_t *row = (volatile uint8_t *)record;
    row[5] = 0u;
    row[6] = 0u;
    row[7] = 0u;
    row[8] = 0u;
    audio_ble_master_row_dispatch_503498(connection_of(message),
                                         audio_ble_comm_profile_slot[4], record);
}

/* Native 0x503820. Security level chooses the row transition mode. */
void audio_ble_master_event_503820(const void *message, void *record)
{
    uint8_t connection = connection_of(message);
    uint8_t security = audio_ble_dm_sec_level_4b71b2(connection);
    if (security != 0u) {
        audio_ble_master_row_dispatch_503498(connection, 0u, record);
    } else if (audio_ble_comm_profile_slot[4] == 0u &&
               ((volatile uint8_t *)record)[8] == 0u) {
        audio_ble_master_row_dispatch_503498(connection, 1u, record);
    }
}
