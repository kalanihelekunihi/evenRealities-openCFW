/* Native image-B 0x1000b958..0x1000bc0c, pinned LVP denoise mode.
 * The native CFG joins the GSC and IMCRA branches at a shared three-frame
 * DRC pass, then emits event 91 and advances the audio budget. All branch
 * conditions, integer widths, live mode words and call order follow the
 * stock instruction trace. DSP children 0xe94c and 0x15d34 remain real
 * source contracts, and hardware/FP timing needs separate qualification.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern void gx8002_image_b_audio_mask_clear_1000a714(void);
extern void gx8002_image_b_audio_mask_set_1000a730(void);
extern uint32_t gx8002_image_b_audio_frame_buffer_address_10009f08(void);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern uint32_t gx8002_image_b_heap_start_10009f10(void);
extern uint32_t gx8002_image_b_audio_word_20_10009f80(void);
extern void *gx8002_image_b_heap_alloc_alias_10009f2c(uint32_t);
extern void *gx8002_image_b_imcra_constructor_1000e784(
    int32_t, int32_t, void *);
extern int32_t gx8002_image_b_denoise_beamforming_init_1000b800(void);
extern int32_t gx8002_image_b_denoise_state_init_1000b91c(void);
extern uint32_t gx8002_image_b_audio_ring_read_10009fbc(
    volatile int32_t *, uint8_t *);
extern uint32_t gx8002_image_b_mic_frame_10009ec0(
    const uint32_t *, uint32_t, uint32_t);
extern void gx8002_image_b_dsp_copy_1000f180(
    const int16_t *, int16_t *, uint32_t);
extern uint32_t gx8002_image_b_dsp_transform_entry_1000de94(
    const void *, void *, uint32_t);
extern void gx8002_image_b_beamforming_process_entry_1000dea0(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern void gx8002_image_b_dcache_clean_range_10004e74(
    uint32_t, int32_t);
extern void gx8002_image_b_mode5_tick_drc_slice(
    const volatile uint32_t *, uint32_t);
extern void gx8002_image_b_mode5_tick_imcra_slice(
    const volatile uint32_t *, uint32_t);
extern void gx8002_image_b_mode5_tick_finish_slice(uint32_t);
extern volatile uint8_t gx8002_image_b_denoise_mode_state_2002d2bc[];
extern volatile int32_t gx8002_image_b_denoise_ring_2002d2d8[];

static uint32_t load_word(const volatile uint8_t *base, uint32_t offset)
{
    return *(const volatile uint32_t *)(const volatile void *)(base + offset);
}

static void store_word(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(volatile void *)(base + offset) = value;
}

static void gsc_frames(volatile uint8_t *state, uint32_t context_address)
{
    const uint32_t *const context = (const uint32_t *)(uintptr_t)context_address;
    const uint32_t *const header = (const uint32_t *)(uintptr_t)context[0];
    int32_t frames = (int32_t)header[0x24u / 4u];
    uint32_t gsc = load_word(state, 0u);
    if (gsc == 0u) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Need init Beamforming\n");
        return;
    }
    if (frames <= 0)
        return;

    int32_t channels = (int32_t)header[0x08u / 4u];
    int32_t context_frames = frames / 3;
    uint32_t clean_bytes =
        (header[0x1cu / 4u] * (uint32_t)frames * 2u *
         header[0x20u / 4u]) / 1000u;
    uint32_t output_index = 0u;
    uint32_t native_event_scratch[2];
    for (int32_t frame = 0; frame < frames; ++frame) {
        uint32_t output = load_word(state, 4u);
        if (channels > 0) {
            uint32_t destination_offset = 512u;
            for (int32_t channel = 0; channel < channels; ++channel) {
                uint32_t input = gx8002_image_b_mic_frame_10009ec0(
                    context, (uint32_t)channel, (uint32_t)frame);
                gx8002_image_b_dsp_copy_1000f180(
                    (const int16_t *)(uintptr_t)input,
                    (int16_t *)(uintptr_t)(output + destination_offset),
                    256u);
                destination_offset += 1024u;
            }
        }
        uint32_t phase = (uint32_t)frame +
            context[8u / 4u] * header[0x24u / 4u];
        (void)gx8002_image_b_dsp_transform_entry_1000de94(
            (const void *)(uintptr_t)load_word(state, 0u),
            (void *)(uintptr_t)output, phase);
        if ((phase + 1u) % 3u != 0u) {
            if (channels > 0) {
                uint32_t offset = 512u;
                for (int32_t channel = 0; channel < channels; ++channel) {
                    gx8002_image_b_dsp_copy_1000f180(
                        (const int16_t *)(uintptr_t)(output + offset),
                        (int16_t *)(uintptr_t)(output + offset - 512u),
                        256u);
                    offset += 1024u;
                }
            }
            continue;
        }
        uint32_t result = gx8002_image_b_mic_frame_10009ec0(
            context, 0u, 0u);
        gx8002_image_b_beamforming_process_entry_1000dea0(
            load_word(state, 0u), result,
            (uint32_t)context_frames, output_index,
            (uint32_t)(uintptr_t)native_event_scratch);
        gx8002_image_b_dcache_clean_range_10004e74(
            result, (int32_t)clean_bytes);
        ++output_index;
    }
}

void gx8002_image_b_mode5_tick_1000b958(void)
{
    volatile uint8_t *const state = gx8002_image_b_denoise_mode_state_2002d2bc;
    uint32_t active = load_word(state, 0x14u);
    if (active != 0u && active != 1u)
        return;
    if (active == 1u) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Exit denoise mode\n");
        gx8002_image_b_audio_mask_clear_1000a714();
        uint32_t base = gx8002_image_b_audio_frame_buffer_address_10009f08();
        gx8002_image_b_zero_100113c4(
            (void *)(uintptr_t)base, 0u, 0x11000u);
        (void)gx8002_image_b_heap_start_10009f10();
        uint32_t rate = gx8002_image_b_audio_word_20_10009f80();
        (void)gx8002_image_b_heap_log_10009934(
            "samplerate %d frame size %d\n", rate, 256u);
        rate = gx8002_image_b_audio_word_20_10009f80();
        void *allocation = gx8002_image_b_heap_alloc_alias_10009f2c(512u);
        void *drc = gx8002_image_b_imcra_constructor_1000e784(
            (int32_t)rate, 256, allocation);
        store_word(state, 0x18u, (uint32_t)(uintptr_t)drc);
        if (drc == 0) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE]FrameDrcStateInit Fail!\n");
            return;
        }
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP_MODE_DENOISE]Init DRC\n");
        uint32_t mode = load_word(state, 0x10u);
        if (mode == 0u) {
            if (gx8002_image_b_denoise_beamforming_init_1000b800() != 0) {
                (void)gx8002_image_b_heap_log_10009934(
                    "[LVP_MODE_DENOISE]_beamformingInit Failed !!!\n");
                return;
            }
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][DOUBLE_MIC_DENOISE]Change Init gsc Beamforming OK\n");
        } else if (mode == 1u) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][SINGLE_MIC_DENOISE]Init Imcra\n");
            if (gx8002_image_b_denoise_state_init_1000b91c() != 0) {
                (void)gx8002_image_b_heap_log_10009934(
                    "[LVP_MODE_DENOISE]_imarcInit Failed !!!\n");
                return;
            }
            store_word(state, 0x10u, 1u);
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][SINGLE_MIC_DENOISE]Change Init Imcra\n");
        } else if (mode == 2u) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP_MODE_DENOISE][ORIGIN_MIC]Change origin mic\n");
        }
        gx8002_image_b_audio_mask_set_1000a730();
        store_word(state, 0x14u, 0u);
    }

    uint32_t context_address;
    if (gx8002_image_b_audio_ring_read_10009fbc(
            gx8002_image_b_denoise_ring_2002d2d8,
            (uint8_t *)(void *)&context_address) == 0u)
        return;
    uint32_t mode = load_word(state, 0x10u);
    if (mode == 0u)
        gsc_frames(state, context_address);
    else if (mode == 1u)
        gx8002_image_b_mode5_tick_imcra_slice(
            (const volatile uint32_t *)(const volatile void *)state,
            context_address);
    if (mode == 0u || mode == 1u)
        mode = load_word(state, 0x10u);
    if (mode == 2u)
        gx8002_image_b_mode5_tick_finish_slice(context_address);
    else
        gx8002_image_b_mode5_tick_drc_slice(
            (const volatile uint32_t *)(const volatile void *)state,
            context_address);
}
