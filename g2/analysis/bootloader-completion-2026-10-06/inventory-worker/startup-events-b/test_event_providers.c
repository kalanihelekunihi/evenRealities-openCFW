/* SPDX-License-Identifier: MIT. Isolated lower-cut providers for comparison. */
#include <stdint.h>

#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))

typedef struct {
    uint32_t kind;
    uint32_t a[10];
} event_cut_record_t;

extern uint8_t native_spot_temperature_range(float value);
extern void native_spot_transition_effect(uint8_t requested, uint8_t current);
extern int native_spot_state_decode(const uint8_t *input, uint32_t *major,
                                    uint32_t *minor);
extern uint32_t native_spot_buck_deepsleep_scan(uint32_t snapshot[4],
                                                uint8_t temperature);
extern uint32_t native_spot_state_transition(uint32_t new_major,
                                             uint32_t old_major,
                                             uint32_t new_minor,
                                             uint32_t old_minor);

volatile uint32_t event_cut_count;
volatile uint32_t event_cut_temp_result;
volatile uint32_t event_cut_decode_status;
volatile uint32_t event_cut_decode_major;
volatile uint32_t event_cut_decode_minor;
volatile uint32_t event_cut_scan_xor[4];
volatile event_cut_record_t event_cut_records[16];

static volatile event_cut_record_t *next_record(uint32_t kind)
{
    uint32_t n = event_cut_count++;
    volatile event_cut_record_t *r = &event_cut_records[n];
    r->kind = kind;
    for (uint32_t i = 0; i < 10; ++i) r->a[i] = 0;
    return r;
}

uint8_t event_child_temperature_range(float value)
{
    union { float f; uint32_t u; } raw;
    raw.f = value;
    volatile event_cut_record_t *r = next_record(1U);
    r->a[0] = raw.u;
#ifdef EVENT_CHILD_CUTS
    (void)value;
    return (uint8_t)event_cut_temp_result;
#else
    return native_spot_temperature_range(value);
#endif
}

void event_child_buck_deepsleep_scan(uint32_t snapshot[4],
                                     uint8_t temperature_category)
{
    volatile event_cut_record_t *r = next_record(2U);
#ifdef EVENT_CHILD_CUTS
    (void)temperature_category;
    for (uint32_t i = 0; i < 4; ++i) {
        r->a[i] = snapshot[i];
        snapshot[i] ^= event_cut_scan_xor[i];
        r->a[4U + i] = snapshot[i];
    }
#else
    for (uint32_t i = 0; i < 4; ++i) r->a[i] = snapshot[i];
    r->a[4] = temperature_category;
    (void)native_spot_buck_deepsleep_scan(snapshot, temperature_category);
    for (uint32_t i = 0; i < 4; ++i) r->a[5U + i] = snapshot[i];
    r->a[9] = U8(0x200271c0U);
#endif
}

void event_child_transition_effect(uint8_t requested, uint8_t current)
{
    volatile event_cut_record_t *r = next_record(3U);
    r->a[0] = requested;
    r->a[1] = current;
#ifndef EVENT_CHILD_CUTS
    native_spot_transition_effect(requested, current);
#endif
}

int event_child_state_decode(const uint32_t snapshot[4], uint8_t temperature_category,
                             uint8_t state, uint8_t auxiliary_category,
                             uint32_t *major, uint32_t *minor)
{
    volatile event_cut_record_t *r = next_record(4U);
    for (uint32_t i = 0; i < 4; ++i) r->a[i] = snapshot[i];
    struct {
        uint32_t words[4];
        uint8_t temperature_category;
        uint8_t state;
        uint8_t auxiliary_category;
    } input;
    for (uint32_t i = 0; i < 4; ++i) input.words[i] = snapshot[i];
    input.temperature_category = temperature_category;
    input.state = state;
    input.auxiliary_category = auxiliary_category;
    r->a[4] = temperature_category;
    r->a[5] = state;
    r->a[6] = auxiliary_category;
#ifdef EVENT_CHILD_CUTS
    *major = event_cut_decode_major;
    *minor = event_cut_decode_minor;
    r->a[7] = event_cut_decode_status;
    r->a[8] = *major;
    r->a[9] = *minor;
    return (int)event_cut_decode_status;
#else
    int status = native_spot_state_decode((const uint8_t *)&input, major, minor);
    r->a[7] = (uint32_t)status;
    r->a[8] = *major;
    r->a[9] = *minor;
    return status;
#endif
}

void event_child_state_transition(uint32_t new_major, uint32_t old_major,
                                  uint32_t new_minor, uint32_t old_minor)
{
    volatile event_cut_record_t *r = next_record(5U);
    r->a[0] = new_major;
    r->a[1] = old_major;
    r->a[2] = new_minor;
    r->a[3] = old_minor;
#ifndef EVENT_CHILD_CUTS
    r->a[4] = native_spot_state_transition(new_major, old_major,
                                            new_minor, old_minor);
#endif
}
