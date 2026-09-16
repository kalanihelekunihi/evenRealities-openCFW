/* SPDX-License-Identifier: MIT
 * Reconstructed backup wrapper at 0x1000b91c. The DSP initializer remains
 * an unresolved implementation; its argument contract is observed here.
 */
#include <stdint.h>
struct denoise_prefix {
    uint32_t beam_state, beam_buffer, imcra_buffer, imcra_state;
};
extern volatile struct denoise_prefix backup_denoise_state;
extern void *backup_allocate(uint32_t bytes);
extern uint32_t backup_pcm_sample_rate(void);
extern uint32_t backup_imcra_state_initialize(uint32_t rate, uint32_t buffer,
                                             uint32_t bytes);
extern int printf(const char *, ...);
const char backup_imcra_error[] __attribute__((section(".rodata.imcra_error"))) =
    "[LVP_MODE_DENOISE]ImcraStateInit Fail!\n";
int open_cfw_gx8002_backup_imcra_initialize(void)
{
    backup_denoise_state.imcra_buffer = (uint32_t)(uintptr_t)backup_allocate(43008);
    uint32_t rate = backup_pcm_sample_rate();
    uint32_t state = backup_imcra_state_initialize(
        rate, backup_denoise_state.imcra_buffer, 43008);
    backup_denoise_state.imcra_state = state;
    if (state) return 0;
    printf(backup_imcra_error);
    return -1;
}
