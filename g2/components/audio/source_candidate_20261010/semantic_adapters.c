#include <stdint.h>

/* The original/source composition receipt binds these names directly to
 * the existing source functions. These C adapters preserve arguments and
 * returns; their extra call instruction is not claimed byte-identical. */
extern uint32_t audio_platform_select(uint32_t, uint32_t, uint8_t *);
extern void audio_spot_timer_initialize(void);
extern void audio_block_current(uint32_t, uint32_t);
extern uint32_t audio_port_mask_set(void);
extern uint32_t audio_wait5(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_ext_request(uint32_t);
extern uint32_t audio_ext_release(uint32_t);
extern void pcm_buck_control(uint32_t);
extern uint32_t audio_clock_release(uint32_t, uint32_t);
extern uint32_t audio_hfrc2_apply(const void *);
extern uint32_t audio_hfrc2_disable(void);
extern uint32_t audio_clock_request(uint32_t, uint32_t);
extern uint32_t audio_hfrc_apply(uint32_t);
extern uint32_t audio_oscillator_control(uint32_t, const void *);

uint32_t callback_select(uint32_t next, uint32_t old, uint8_t *index) {
    return audio_platform_select(next, old, index);
}
void platform_finish_init(void) {
    audio_spot_timer_initialize();
}
void audio_block_ticks(uint32_t ticks, uint32_t can_block_indefinitely) {
    audio_block_current(ticks, can_block_indefinitely);
}
uint32_t audio_heap_mask_interrupts(void) {
    return audio_port_mask_set();
}
uint32_t stock_wait5(uint32_t budget, uint32_t address, uint32_t mask,
                     uint32_t expected, uint32_t equal) {
    return audio_wait5(budget, address, mask, expected, equal);
}
uint32_t stock_ext_request(uint32_t user) {
    return audio_ext_request(user);
}
uint32_t stock_ext_release(uint32_t user) {
    return audio_ext_release(user);
}
/* Current unresolved callers are the early PCM pending/GPU sources, whose
 * receipts bind this alias to original 0x47fe6c. A separate transition
 * receipt used the same alias for 0x47f11c; no transition source in this
 * archive calls stock_buck_enable. */
void stock_buck_enable(uint32_t enable) {
    pcm_buck_control(enable);
}
uint32_t stock_clock_release(uint32_t clock, uint32_t user) {
    return audio_clock_release(clock, user);
}
uint32_t stock_hfrc2_apply(const void *config) {
    return audio_hfrc2_apply(config);
}
uint32_t stock_hfrc2_disable(void) {
    return audio_hfrc2_disable();
}
uint32_t stock_clock_request(uint32_t clock, uint32_t user) {
    return audio_clock_request(clock, user);
}
uint32_t stock_hfrc_apply(uint32_t config) {
    return audio_hfrc_apply(config);
}
uint32_t stock_oscillator(uint32_t action, const void *arguments) {
    return audio_oscillator_control(action, arguments);
}
