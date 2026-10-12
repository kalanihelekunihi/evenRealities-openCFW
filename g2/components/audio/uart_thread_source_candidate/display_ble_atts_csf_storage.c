/* Pinned Cordio attsCsfCb_t BSS at native 0x20073e04. Three 2-byte client
 * rows, 2-byte alignment, 4-byte callback, 1-byte hash-update status. */
#include <stdint.h>
typedef struct {
    uint8_t csf;
    uint8_t change_aware_state;
} audio_atts_csf_row_t;
typedef struct {
    audio_atts_csf_row_t rows[3];
    uint8_t alignment[2];
    void (*write_callback)(void);
    uint8_t hash_updating;
    uint8_t trailing_alignment[3];
} audio_atts_csf_state_t;
_Static_assert(sizeof(audio_atts_csf_state_t)==16u,"native attsCsfCb_t size");
_Static_assert(__builtin_offsetof(audio_atts_csf_state_t,write_callback)==8u,"native callback offset");
_Static_assert(__builtin_offsetof(audio_atts_csf_state_t,hash_updating)==12u,"native hash status offset");
audio_atts_csf_state_t audio_ble_connection_state_table;
