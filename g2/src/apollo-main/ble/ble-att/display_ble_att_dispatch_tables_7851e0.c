/* Cordio ATT no-op dispatch tables, stock ROM 0x7851e0..0x7851ff.
 * Each target at 0x4b4ee6/e8/ea/ec is a standalone BX LR body. */
#include <stdint.h>

extern void audio_ble_atts_callback_4b4ee6(void);
void audio_ble_att_noop_4b4ee8(void) {}
void audio_ble_att_noop_4b4eea(void) {}
void audio_ble_att_noop_4b4eec(void) {}

void (*const audio_ble_att_table_main[4])(void) = {
    audio_ble_att_noop_4b4eec,
    audio_ble_atts_callback_4b4ee6,
    audio_ble_atts_callback_4b4ee6,
    audio_ble_att_noop_4b4ee8,
};
void (*const audio_ble_att_table_secondary[4])(void) = {
    audio_ble_att_noop_4b4eea,
    audio_ble_att_noop_4b4eea,
    audio_ble_atts_callback_4b4ee6,
    audio_ble_att_noop_4b4ee8,
};
_Static_assert(sizeof(audio_ble_att_table_main) == 16u, "Cordio ATT main table ABI");
_Static_assert(sizeof(audio_ble_att_table_secondary) == 16u,
               "Cordio ATT secondary table ABI");
