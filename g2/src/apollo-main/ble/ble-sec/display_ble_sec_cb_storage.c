/* Source-owned Cordio secCb BSS, native RAM base 0x20072cb8.
 * Pinned sec_main.h defines 32 random bytes, three 8-byte WSF queues,
 * token/top/bottom, then five 4-byte HCI callback slots. Final linker
 * placement at the native address is a separate image-layout gate. */
#include <stdint.h>
#include <stddef.h>
struct audio_ble_sec_cb {
    uint8_t random[32];
    struct { void *head; void *tail; } aes, public_key, dh_key;
    uint8_t token, random_top, random_bottom, padding;
    void (*callbacks[5])(void);
};
_Static_assert(offsetof(struct audio_ble_sec_cb,aes)==0x20u,"AES queue ABI");
_Static_assert(offsetof(struct audio_ble_sec_cb,token)==0x38u,"token ABI");
_Static_assert(offsetof(struct audio_ble_sec_cb,callbacks)==0x3cu,"callback ABI");
_Static_assert(sizeof(struct audio_ble_sec_cb)==0x50u,"secCb extent");
struct audio_ble_sec_cb audio_ble_stack_state_20072cb8;
