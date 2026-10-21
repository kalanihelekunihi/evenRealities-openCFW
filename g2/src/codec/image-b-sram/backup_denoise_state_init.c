/* SPDX-License-Identifier: MIT
 * Image-B denoise state allocation 0x1000b91c..0x1000b94d.
 * Native record literal at 0x1000b950: 0x2002d2bc; the exact failure
 * message resides at 0x1001378c. The Imcra initializer at 0x1000e384 is
 * a genuine descendant contract until its full body is source-reduced.
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

extern void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t bytes);
extern uint32_t gx8002_image_b_audio_word_20_10009f80(void);
extern int32_t gx8002_image_b_imcra_state_init_1000e384(
    uint32_t sample_word, void *allocation, uint32_t bytes);
extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

int32_t gx8002_image_b_denoise_state_init_1000b91c(void)
{
    volatile uint32_t *state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d2bc);
    void *allocation = gx8002_image_b_heap_alloc_alias_10009f2c(43008u);
    state[2] = (uint32_t)(uintptr_t)allocation;
    uint32_t sample_word = gx8002_image_b_audio_word_20_10009f80();
    int32_t result = gx8002_image_b_imcra_state_init_1000e384(
        sample_word, allocation, 43008u);
    state[3] = (uint32_t)result;
    if (result != 0) return 0;
    (void)gx8002_image_b_heap_log_10009934(
        "[LVP_MODE_DENOISE]ImcraStateInit Fail!\n");
    return -1;
}
