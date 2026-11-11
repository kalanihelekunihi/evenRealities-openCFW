/* Stock 0x7c9e8 and 0x628cc: ring-size KV update and legacy reply. */
#include <stdint.h>
#include "native_kv_class.h"

extern void *volatile r1_r_size_kv_handle;
extern uint32_t r1_nv_modules_idle_check(void);
extern uint32_t r1_batcfg_byte_rec8_get(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

uint32_t r1_kv_r_size_set(uint32_t value)
{
    uint8_t record = 0u;
    (void)r1_kv_class_read(r1_r_size_kv_handle, &record, 1u);
    record = (uint8_t)value;
    (void)r1_kv_class_write(r1_r_size_kv_handle, &record, 1u);
    return r1_nv_modules_idle_check();
}

uint32_t r1_legacy_cmd_ring_size_reply(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] == 1u)
        (void)r1_kv_r_size_set(bytes[4]);
    else if (bytes[3] != 0u)
        return 0u;
    bytes[4] = (uint8_t)r1_batcfg_byte_rec8_get();
    return r1_legacy_bounded_reply_send(packet, 5u);
}
