/* Stock 0x67e4c: accelerometer window feature classifier. */
#include "native_gomore_accel_features.h"
#include "native_gomore_accel_class_helpers.h"
#include "native_gomore_accel_ring_predicates.h"
#include "native_gomore_accel_axis_gate.h"
#include "native_gomore_accel_ring_score.h"
#include "native_gomore_accel_crossing.h"
#include "native_gomore_accel_autocorrelation.h"
#include <stddef.h>

static uint32_t address(const volatile void *p) { return (uint32_t)(uintptr_t)p; }
static uint32_t cursor(uint32_t state) {
    return (uint32_t)(int32_t)*(volatile int8_t *)(uintptr_t)(state+0x52u);
}
static void put_float(uint32_t p, float value) {
    *(volatile float *)(uintptr_t)p = value;
}
static int32_t word(uint32_t p) { return *(volatile int32_t *)(uintptr_t)p; }

uint32_t r1_gomore_accel_features_native(uint32_t state, uint32_t output) {
    volatile float crossing1 = 0.0f, crossing2 = 0.0f;
    volatile uint32_t counts = 0;
    volatile float shape[2] = {0.0f,0.0f};
    volatile int32_t recent[3] = {0,0,0};
    float ratio = 0.0f;
    put_float(output+8u,r1_gomore_accel_nonzero_mean8_native(state+0x32u));
    put_float(output+12u,r1_gomore_accel_nonzero_mean8_native(state+0x12u));
    put_float(output+4u,r1_gomore_accel_nonzero_mean8_native(state+2u));
    put_float(output,r1_gomore_accel_nonzero_mean8_native(state+0x22u));
    uint32_t primary = r1_gomore_accel_band_count_native(state+0x42u,8,cursor(state),5,130,20000,0x3e,3);
    (void)r1_gomore_accel_autocorrelation_wrapper_native(primary,
        (const uint16_t *)(uintptr_t)(state+0xeau),
        (float *)(uintptr_t)(output+0x20u),(float *)(uintptr_t)(output+0x28u),
        (float *)(uintptr_t)(output+0x2cu),(float *)(uintptr_t)(output+0x30u),
        (float *)(uintptr_t)(output+0x34u),address(&counts),address(shape));
    uint32_t crossings = 0;
    if (primary == 1u) {
        crossings = r1_gomore_accel_hysteresis_count_native(state+0x54u,200);
        (void)r1_gomore_accel_crossing_native(state,state+0x54u,address(&crossing2),address(&crossing1));
    }
    /* Stock compares signed encodings here, not floating-point values. */
    if ((word(output)<INT32_C(0x43160000) && word(address(&crossing1))>INT32_C(0x43020000)) ||
        (word(output+8u)<INT32_C(0x44898000) && crossings<13u && word(address(&crossing1))>INT32_C(0x43020000))) {
        crossing1 = crossing1 * 0.5f;
    }
    put_float(output+0x10u,crossing1);
    put_float(output+0x14u,crossing2);
    (void)r1_gomore_accel_recent_mean3_native(state+2u,state+0x204u,state+0x214u,8,cursor(state),3,
        address(&recent[0]),address(&recent[1]),address(&recent[2]));
    *(volatile uint8_t *)(uintptr_t)(output+0x38u) = (uint8_t)primary;
    if (*(volatile float *)(uintptr_t)(output+0x28u) <= 0.0f) {
        *(volatile uint8_t *)(uintptr_t)(output+0x3du)=255;
    } else {
        int32_t count=(int8_t)(uint8_t)counts;
        if (count != 0) ratio=(float)(int8_t)(uint8_t)(counts>>8)/(float)count;
        *(volatile uint8_t *)(uintptr_t)(output+0x3du)=(uint8_t)
            r1_gomore_accel_linear_classify_native(shape[0],shape[1],ratio,(uint32_t)count);
    }
    *(volatile uint8_t *)(uintptr_t)(output+0x39u)=(uint8_t)
        r1_gomore_accel_activity_gate_native(state+0x42u,state+2u,state+0x204u,state+0x214u,8,cursor(state),5);
    uint32_t score=r1_gomore_accel_ring_score_native(state+0x42u,state+0x22u,state+0x224u,
        state+0x234u,state+0x244u,state+0x254u,8,cursor(state),3);
    *(volatile uint8_t *)(uintptr_t)(output+0x3au)=(uint8_t)r1_gomore_accel_recent_decision_native(state,score);
    *(volatile uint8_t *)(uintptr_t)(output+0x3bu)=(uint8_t)
        r1_gomore_accel_band_count_native(state+0x42u,8,cursor(state),5,1900,20000,0x3e,3);
    *(volatile uint8_t *)(uintptr_t)(output+0x3cu)=(uint8_t)
        r1_gomore_accel_axis_gate_native(state+2u,state+0x204u,state+0x214u,8,cursor(state),5,400,400);
    return 0;
}
