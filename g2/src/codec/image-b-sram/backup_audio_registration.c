/* SPDX-License-Identifier: MIT
 * Image-B 0x1000a418 registration path. Native callback and RAM addresses
 * are retained as typed contracts; the mode at heap-end +4 is not initialized
 * by this function.
 */
#include <stdint.h>

typedef int32_t (*audio_config_callback)(void);
typedef int32_t (*audio_stream_callback)(uint32_t, uint32_t *);
typedef int32_t (*audio_event_callback)(uint32_t);
typedef struct {
    audio_stream_callback record_callback;
    audio_config_callback config_callback;
    audio_stream_callback update_callback;
    audio_event_callback engvad_callback;
    audio_event_callback fftvad_callback;
} audio_config;

extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern int32_t gx8002_image_b_clock_module_select_100035c0(uint32_t, uint32_t);
extern int32_t gx8002_image_b_audio_init_10005ce8(audio_config);
extern int32_t gx8002_image_b_audio_record_10015bc8(uint32_t, uint32_t *);
extern int32_t gx8002_image_b_audio_configure_1000a2a0(void);

/* The native entry at 0x1000a030 consists solely of an instruction returning
 * to the caller. The audio-init path stores this callback without calling it. */
__attribute__((naked)) int32_t gx8002_image_b_audio_update_1000a030(
    uint32_t ignored __attribute__((unused)),
    uint32_t *unused __attribute__((unused)))
{
    __asm__ volatile ("jmp r15");
}

int32_t gx8002_image_b_audio_register_1000a418(uint32_t input)
{
    audio_config config = {
        .record_callback = gx8002_image_b_audio_record_10015bc8,
        .config_callback = gx8002_image_b_audio_configure_1000a2a0,
        .update_callback = gx8002_image_b_audio_update_1000a030,
        .engvad_callback = 0,
        .fftvad_callback = 0,
    };
    gx8002_image_b_zero_100113c4((void *)(uintptr_t)UINT32_C(0x2002d75c), 0u, 20u);
    (void)gx8002_image_b_clock_module_select_100035c0(8u, 7u);
    int32_t result = gx8002_image_b_audio_init_10005ce8(config);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cb80) = input;
    /* Native 0xa452..0xa458 leaves the audio-init R0 live across this store.
     * The denoise-mode initializer at 0xbc4e branches on that exact result. */
    return result;
}
