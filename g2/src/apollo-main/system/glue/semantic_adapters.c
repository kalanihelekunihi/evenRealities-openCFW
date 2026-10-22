#include <stdint.h>

/* The original/source composition receipt binds these names directly to
 * the existing source functions. These C adapters preserve arguments and
 * returns; their extra call instruction is not claimed byte-identical.
 * Adapters whose target is defined in the payload are payload defsym
 * aliases instead (callback_select, stock_ext_request/release,
 * stock_clock_request/release, stock_oscillator); the ones below remain
 * because their targets are not yet defined by any unit. */
extern void audio_spot_timer_initialize(void);
extern uint32_t audio_wait5(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_hfrc2_apply(const void *);
extern uint32_t audio_hfrc2_disable(void);
extern uint32_t audio_hfrc_apply(uint32_t);

void platform_finish_init(void) {
    audio_spot_timer_initialize();
}
uint32_t stock_wait5(uint32_t budget, uint32_t address, uint32_t mask,
                     uint32_t expected, uint32_t equal) {
    return audio_wait5(budget, address, mask, expected, equal);
}
/* stock_buck_enable (callers bound to stock 0x47fe6c) is upstream
 * buck_ldo_update_override in the am_hal_pwrctrl.c unit (payload defsym). */
uint32_t stock_hfrc2_apply(const void *config) {
    return audio_hfrc2_apply(config);
}
uint32_t stock_hfrc2_disable(void) {
    return audio_hfrc2_disable();
}
uint32_t stock_hfrc_apply(uint32_t config) {
    return audio_hfrc_apply(config);
}
