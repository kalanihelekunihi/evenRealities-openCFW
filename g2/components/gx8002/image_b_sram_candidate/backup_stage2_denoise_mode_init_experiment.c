/* Stock image-B 0x1000bc44..0x1000bd1a, denoise mode initializer.
 * CFG and exact product log strings come from the native image; pinned
 * NationalChip lvp/lvp_mode_denoise.c corroborates queue/GSC/IMCRA/audio
 * phases. The mode prefix, queue and queue buffer have separate BSS objects.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_platform_status_10003fb8(void);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern void gx8002_image_b_audio_frame_set_10009fa8(
    uint32_t *, uint32_t, int32_t, int32_t);
extern uint32_t gx8002_image_b_heap_start_10009f10(void);
extern int32_t gx8002_image_b_denoise_beamforming_init_1000b800(void);
extern int32_t gx8002_image_b_denoise_state_init_1000b91c(void);
extern uint32_t gx8002_image_b_audio_word_20_10009f80(void);
extern void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t);
extern void *gx8002_image_b_imcra_constructor_1000e784(int32_t, int32_t, void *);
extern int32_t gx8002_image_b_audio_register_1000a418(uint32_t);
extern int32_t gx8002_image_b_denoise_audio_callback_1000bd54(uint32_t, void *);
extern volatile uint8_t gx8002_image_b_denoise_mode_state_2002d2bc[];
extern volatile int32_t gx8002_image_b_denoise_ring_2002d2d8[5];
extern volatile uint8_t gx8002_image_b_denoise_queue_buffer_2002d2f0[40];

int32_t gx8002_image_b_mode5_init_1000bc44(uint32_t mode)
{
    (void)mode;
    volatile uint8_t *const state = gx8002_image_b_denoise_mode_state_2002d2bc;
    if (gx8002_image_b_platform_status_10003fb8() < 2u) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Init denoise mode\n");
        gx8002_image_b_audio_frame_set_10009fa8(
            (uint32_t *)(void *)gx8002_image_b_denoise_ring_2002d2d8,
            (uint32_t)(uintptr_t)gx8002_image_b_denoise_queue_buffer_2002d2f0,
            40, 4);
        (void)gx8002_image_b_heap_start_10009f10();
        uint32_t type = *(volatile uint32_t *)(void *)(state + 0x10u);
        if (type == 0u) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][DOUBLE_MIC_DENOISE]Init gsc Beamforming\n");
            if (gx8002_image_b_denoise_beamforming_init_1000b800() != 0) {
                (void)gx8002_image_b_heap_log_10009934(
                    "[LVP_MODE_DENOISE]_beamformingInit Failed !!!\n");
                return -1;
            }
        } else if (type == 1u) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][SINGLE_MIC_DENOISE]Init Imcra\n");
            if (gx8002_image_b_denoise_state_init_1000b91c() != 0) {
                (void)gx8002_image_b_heap_log_10009934(
                    "[LVP_MODE_DENOISE]_imarcInit Failed !!!\n");
                return -1;
            }
        } else {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE]No noise reduction\n");
        }
        uint32_t sample = gx8002_image_b_audio_word_20_10009f80();
        (void)gx8002_image_b_heap_log_10009934(
            "samplerate %d frame size %d\n", sample, 256u);
        sample = gx8002_image_b_audio_word_20_10009f80();
        void *allocation = gx8002_image_b_heap_alloc_alias_10009f2c(512u);
        void *drc = gx8002_image_b_imcra_constructor_1000e784(
            (int32_t)sample, 256, allocation);
        *(volatile uint32_t *)(void *)(state + 0x18u) = (uint32_t)(uintptr_t)drc;
        if (drc == 0) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE]FrameDrcStateInit Fail!\n");
            return -1;
        }
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Init DRC\n");
    }

    int32_t result = gx8002_image_b_audio_register_1000a418(
        (uint32_t)(uintptr_t)gx8002_image_b_denoise_audio_callback_1000bd54);
    if (result != 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]LvpAudioInInit Failed !!!\n");
        return -1;
    }
    (void)gx8002_image_b_heap_log_10009934(
        "[LVP_MODE_DENOISE]LvpAudioInInit OK!!!\n");
    (void)gx8002_image_b_heap_log_10009934(
        "[LVP_MODE_DENOISE]Denoise Init OK!!!\n");
    return 0;
}
