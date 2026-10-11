/* SPDX-License-Identifier: MIT
 * Image-A XIP audio input lifecycle 0x102073bc/0x102073f8.
 * Board configuration and audio hardware lower bodies retain their own
 * source contracts; product pointer identities are native literals.
 */
#include <stdint.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_initialize_102047e4(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_exit_10204984(void);
extern uint32_t gx8002_resident_audio_record_callback_26214(void);
extern uint32_t gx8002_xip_audio_input_config_10207234(void);

/* Native 0x10207020 is exactly `jmp r15`. */
void gx8002_xip_audio_input_irq_10207020(void) {}

uint32_t gx8002_xip_audio_input_initialize_102073bc(
    uint32_t (*callback)(int32_t))
{
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002ecb0), 0u, 20u);
    uint32_t result = gx8002_xip_audio_initialize_102047e4(
        (uint32_t)(uintptr_t)gx8002_resident_audio_record_callback_26214,
        (uint32_t)(uintptr_t)gx8002_xip_audio_input_config_10207234,
        (uint32_t)(uintptr_t)gx8002_xip_audio_input_irq_10207020,
        0u, 0u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfa0) =
        (uint32_t)(uintptr_t)callback;
    return result;
}

uint32_t gx8002_xip_audio_input_done_102073f8(void)
{
    (void)gx8002_xip_audio_exit_10204984();
    return 0u;
}
