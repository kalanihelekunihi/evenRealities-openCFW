/* Stock 0x629d4, 0x90fac, 0x6f228, and 0x6f304. */
#include <stdint.h>
#include <stddef.h>
#include "../runtime/native_factory_mode.h"

extern volatile uint32_t r1_factory_reset_cache[3];
extern uint32_t r1_sensor_stream_register_by_name(
    const char *, const char *, uintptr_t, uint32_t, uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *, uint32_t);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);
extern uint32_t r1_kv_nv_r1_field_set_a(const void *);
extern void __aeabi_memclr(void *, size_t);

/* Native fields at 0x20006c54 and 0x20006c5a, outside the 28-byte
 * factory-mode prefix. The source linker owns these six-byte records. */
volatile int16_t r1_factory_orientation_result[3]
    __attribute__((section(".r1.factory.orientation.result"),aligned(2)));
volatile uint16_t r1_factory_first_sample[3]
    __attribute__((section(".r1.factory.first.sample"),aligned(2)));

static uint16_t count_get(void)
{
    volatile uint8_t *p = &r1_factory_mode_state.reserved[5];
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}
static void count_set(uint16_t value)
{
    volatile uint8_t *p = &r1_factory_mode_state.reserved[5];
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
}
static uint16_t sample16(const uint8_t *bytes)
{
    return (uint16_t)(bytes[0] | ((uint16_t)bytes[1] << 8));
}

/* Stock 0x6f304: regular factory stream callback. Calibration mode retains
 * the first sample; ordinary mode reports it immediately. */
void r1_factory_acc_sample_callback(uint32_t source, const void *payload)
{
    (void)source;
    if (!payload) return;
    const uint8_t *samples = payload;
    if (!sample16(samples + 180)) return;
    if (r1_factory_mode_state.active) {
        for (uint32_t axis = 0; axis < 3; ++axis)
            r1_factory_first_sample[axis] = sample16(samples + axis * 2u);
        return;
    }
    uint8_t reply[36];
    __aeabi_memclr(reply, sizeof(reply));
    reply[1] = 1u;
    reply[2] = 0x40u;
    reply[3] = 4u;
    for (uint32_t i = 0; i < 6; ++i)
        reply[4u + i] = samples[i];
    (void)r1_legacy_bounded_reply_send(reply, 10u);
}

/* Stock 0x6f228: sum at most 100 triples, then save the orientation
 * calibration and close the one-shot accelerometer listener. */
void r1_motion_orientation_accumulator(uint32_t source, const void *payload)
{
    (void)source;
    const uint8_t *samples = payload;
    uint16_t length = sample16(samples + 180);
    for (uint8_t i = 0; i < length; ++i) {
        uint16_t count = count_get();
        if (count >= 100u) break;
        for (uint32_t axis = 0; axis < 3; ++axis) {
            int32_t value = (int16_t)sample16(samples + 6u * i + 2u * axis);
            r1_factory_reset_cache[axis] += (uint32_t)value;
        }
        count_set((uint16_t)(count + 1u));
    }
    if (count_get() < 100u) return;

    int32_t x = (int32_t)r1_factory_reset_cache[0] / 100;
    int32_t y = (int32_t)r1_factory_reset_cache[1] / 100;
    int32_t z = (int32_t)r1_factory_reset_cache[2] / 100;
    r1_factory_orientation_result[0] = (int16_t)-x;
    r1_factory_orientation_result[1] = (int16_t)(y > 0 ? 1024 - y : -1024 - y);
    r1_factory_orientation_result[2] = (int16_t)-z;
    uint8_t field[6];
    for (uint32_t axis = 0; axis < 3; ++axis) {
        uint16_t value = (uint16_t)r1_factory_orientation_result[axis];
        field[axis * 2u] = (uint8_t)value;
        field[axis * 2u + 1u] = (uint8_t)(value >> 8);
    }
    (void)r1_kv_nv_r1_field_set_a(field);

    uint8_t reply[36];
    __aeabi_memclr(reply, sizeof(reply));
    reply[1] = 1u;
    reply[2] = 0x40u;
    reply[3] = 10u;
    reply[4] = 1u;
    (void)r1_legacy_bounded_reply_send(reply, 5u);
    r1_sensor_stream_unregister_by_name("acc", r1_factory_mode_state.acc);
    r1_factory_mode_state.acc = 0u;
    r1_factory_mode_state.reserved[0] = 0u;
    r1_factory_reset_cache[2] = 0u;
    r1_factory_reset_cache[1] = 0u;
    r1_factory_reset_cache[0] = 0u;
    count_set(0u);
}

/* Stock 0x90fac: reset the accumulator before registering the one-shot
 * calibration callback. */
void r1_factory_acc_listener_register(void)
{
    r1_factory_reset_cache[0] = 0u;
    r1_factory_reset_cache[1] = 0u;
    r1_factory_reset_cache[2] = 0u;
    count_set(0u);
    r1_factory_mode_state.reserved[0] = 1u;
    r1_factory_mode_state.acc = r1_sensor_stream_register_by_name(
        "acc", "factory", (uintptr_t)r1_motion_orientation_accumulator, 1u, 0u);
}

/* Stock 0x629d4: factory aging stream control. */
uint32_t r1_factory_aging_stream_command(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = packet;
    if (r1_factory_mode_state.active) {
        bytes[4] = 0xffu;
        return r1_legacy_bounded_reply_send(bytes, 5u);
    }
    uint8_t selector = bytes[3];
    uint32_t stream = r1_factory_mode_state.acc;
    if (selector == 4u) {
        if (!stream)
            r1_factory_mode_state.acc = r1_sensor_stream_register_by_name(
                "acc", "factory", (uintptr_t)r1_factory_acc_sample_callback, 1u, 0u);
        return 0u;
    }
    if (selector == 10u) {
        if (!stream) {
            r1_factory_acc_listener_register();
            return 0u;
        }
        bytes[4] = 0u;
        return r1_legacy_bounded_reply_send(bytes, 5u);
    }
    if (selector == 0u) {
        if (stream) {
            r1_sensor_stream_unregister_by_name("acc", stream);
            r1_factory_mode_state.acc = 0u;
            if (r1_factory_mode_state.reserved[0]) {
                r1_factory_mode_state.reserved[0] = 0u;
                r1_factory_reset_cache[0] = 0u;
                r1_factory_reset_cache[1] = 0u;
                r1_factory_reset_cache[2] = 0u;
                count_set(0u);
            }
            bytes[4] = 1u;
        } else {
            bytes[4] = 0u;
        }
        return r1_legacy_bounded_reply_send(bytes, 5u);
    }
    return 0u;
}
