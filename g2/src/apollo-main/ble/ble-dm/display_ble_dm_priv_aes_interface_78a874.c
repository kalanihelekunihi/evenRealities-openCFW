/* Cordio privacy AES interface 0x78a874 and action table 0x78d454.
 * dmPrivCb's pinned layout through genAddrBuf is 26 bytes at 0x20073a58. */
#include <stddef.h>
#include <stdint.h>

extern void audio_ble_dm_empty_reset_4d29be(void);
extern void audio_ble_dm_empty_handler_4d29c0(void *);
extern uint8_t audio_ble_dm_handler_state[]; /* native dmCb 0x20073b78 */
extern int memcmp(const void *, const void *, size_t);
extern void *memcpy(void *, const void *, size_t);

uint8_t audio_ble_dm_priv_cb_storage[26u];
typedef void (*audio_ble_dm_priv_fn)(void *);
typedef void (*audio_ble_dm_event_callback)(void *);

static void audio_ble_dm_priv_aes_resolve_4d25ba(void *message_ptr)
{
    uint8_t *const message = (uint8_t *)message_ptr;
    const void *const ciphertext = *(const void **)(const void *)(message + 4u);
    message[3u] = memcmp(audio_ble_dm_priv_cb_storage, ciphertext, 3u) == 0 ? 0u : 5u;
    audio_ble_dm_priv_cb_storage[3u] &= (uint8_t)~1u;
    message[2u] = 0x37u;
    (*(audio_ble_dm_event_callback *)(void *)(audio_ble_dm_handler_state + 8u))(message);
}

static void audio_ble_dm_priv_aes_generate_4d26ac(void *message_ptr)
{
    uint8_t *const message = (uint8_t *)message_ptr;
    const void *const ciphertext = *(const void **)(const void *)(message + 4u);
    (void)memcpy(message + 4u, ciphertext, 3u);
    (void)memcpy(message + 7u, audio_ble_dm_priv_cb_storage + 10u, 3u);
    audio_ble_dm_priv_cb_storage[3u] &= (uint8_t)~2u;
    message[2u] = 0x38u;
    message[3u] = 0u;
    (*(audio_ble_dm_event_callback *)(void *)(audio_ble_dm_handler_state + 8u))(message);
}

const audio_ble_dm_priv_fn audio_ble_dm_priv_aes_actions[2]
    __attribute__((used, aligned(4))) = {
        audio_ble_dm_priv_aes_resolve_4d25ba,
        audio_ble_dm_priv_aes_generate_4d26ac,
    };

void audio_ble_dm_priv_aes_msg_handler_4d27ce(void *message_ptr)
{
    const uint8_t *const message = (const uint8_t *)message_ptr;
    audio_ble_dm_priv_aes_actions[message[2u] & 7u](message_ptr);
}

const audio_ble_dm_priv_fn audio_ble_dm_priv_table_b[3]
    __attribute__((used, aligned(4))) = {
        (audio_ble_dm_priv_fn)audio_ble_dm_empty_reset_4d29be,
        audio_ble_dm_empty_handler_4d29c0,
        audio_ble_dm_priv_aes_msg_handler_4d27ce,
    };
