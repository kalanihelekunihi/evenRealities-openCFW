/* Native Cordio LESC interface 0x78a8a4, message handler 0x534894.
 * The OOB random pointer is native RAM 0x200744f8; final placement is open. */
#include <stdint.h>

extern void audio_ble_dm_empty_reset_4d29be(void);
extern void audio_ble_dm_empty_handler_4d29c0(void *);
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern void WsfBufFree(void *);
extern void Calc128Cpy(void *, const void *);

uint8_t *audio_ble_dm_lesc_oob_rand;

typedef void (*audio_ble_dm_event_callback)(void *);
void audio_ble_dm_lesc_msg_handler_534894(void *message_ptr)
{
    uint8_t *const message = (uint8_t *)message_ptr;
    audio_ble_dm_event_callback const callback =
        *(audio_ble_dm_event_callback *)(void *)(audio_ble_dm_handler_state + 8u);
    if (message[2u] == 0x41u) {
        message[2u] = 0x34u;
        callback(message);
    } else if (message[2u] == 0x40u) {
        uint8_t indication[36];
        WsfBufFree(*(void **)(void *)(message + 8u));
        indication[2u] = 0x33u;
        indication[3u] = 0u;
        Calc128Cpy(indication + 4u, *(const void **)(const void *)(message + 4u));
        Calc128Cpy(indication + 20u, audio_ble_dm_lesc_oob_rand);
        WsfBufFree(audio_ble_dm_lesc_oob_rand);
        callback(indication);
    }
}

typedef void (*audio_ble_dm_lesc_fn)(void *);
_Static_assert(sizeof(audio_ble_dm_lesc_fn) == 4u, "Thumb pointer ABI");
const audio_ble_dm_lesc_fn audio_ble_dm_lesc_table[3]
    __attribute__((used, aligned(4))) = {
        (audio_ble_dm_lesc_fn)audio_ble_dm_empty_reset_4d29be,
        audio_ble_dm_empty_handler_4d29c0,
        audio_ble_dm_lesc_msg_handler_534894,
    };
