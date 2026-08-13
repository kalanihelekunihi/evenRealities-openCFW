#include "openr1/r1_runtime.h"

/*
 * Freestanding nRF52840/S140 runtime boundary. Board peripherals remain
 * separate provider/port work; the BLE service binds its
 * transmitter after the SoftDevice and attribute table have been enabled.
 */

static r1_runtime runtime;

void openr1_platform_initialize(void) {
    r1_runtime_initialize(&runtime, NULL, NULL);
}

r1_runtime *openr1_platform_runtime(void) {
    return &runtime;
}

uint32_t openr1_platform_poll(uint32_t now_tick) {
    return r1_runtime_poll(&runtime, now_tick);
}
