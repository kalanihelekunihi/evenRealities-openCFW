/* Native image-B 0x1000b9da..0x1000ba68 and 0x1000bb7c..0x1000bbbc.
 * These complete mode-1/mode-2 processing slices are retained separately
 * while the mode-0 GSC channel loop and 0xb958 entry are reconstructed.
 * The two DSP children remain genuine callable contracts.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_mic_frame_10009ec0(
    const uint32_t *, uint32_t, uint32_t);
extern uint32_t gx8002_image_b_audio_frame_address_10009e50(uint32_t);
extern void gx8002_image_b_drc_process_1000e94c(
    uint32_t state, uint32_t samples, float gain);
extern void gx8002_image_b_imcra_process_10015d34(
    uint32_t state, uint32_t input, uint32_t output);
extern void gx8002_image_b_dcache_clean_range_10004e74(
    uint32_t address, int32_t bytes);
extern int32_t gx8002_image_b_audio_uart_ring_enqueue_1000bde8(
    const uint8_t *event);
extern uint32_t gx8002_image_b_audio_budget_advance_1000a3fc(uint32_t);

static uint32_t word(const void *record, uint32_t offset)
{
    return *(const uint32_t *)(const void *)((const uint8_t *)record + offset);
}

void gx8002_image_b_mode5_tick_finish_slice(
    uint32_t context_address)
{
    uint32_t event[2] = {91u,
        word((const void *)(uintptr_t)context_address, 8u)};
    (void)gx8002_image_b_audio_uart_ring_enqueue_1000bde8(
        (const uint8_t *)(const void *)event);
    (void)gx8002_image_b_audio_budget_advance_1000a3fc(1u);
}

void gx8002_image_b_mode5_tick_drc_slice(
    const volatile uint32_t *mode_state, uint32_t context_address)
{
    const uint32_t *const context = (const uint32_t *)(uintptr_t)context_address;
    const uint32_t *const header = (const uint32_t *)(uintptr_t)context[0];
    uint32_t first = gx8002_image_b_mic_frame_10009ec0(
        context, 0u, 0u);
    uint32_t per_frame =
        (header[0x1cu / 4u] * header[0x20u / 4u]) / 1000u;
    uint32_t current = first;
    for (unsigned step = 0; step < 3u; ++step) {
        gx8002_image_b_drc_process_1000e94c(
            mode_state[0x18u / 4u], current,
            (float)(int32_t)mode_state[0x30u / 4u]);
        current += per_frame * 2u;
    }
    gx8002_image_b_dcache_clean_range_10004e74(
        first, (int32_t)(per_frame * 6u));
    gx8002_image_b_mode5_tick_finish_slice(context_address);
}

void gx8002_image_b_mode5_tick_imcra_slice(
    const volatile uint32_t *mode_state, uint32_t context_address)
{
    const uint32_t *const context = (const uint32_t *)(uintptr_t)context_address;
    const uint32_t *const header = (const uint32_t *)(uintptr_t)context[0];
    uint32_t output = gx8002_image_b_audio_frame_address_10009e50(
        context[8u / 4u]);
    uint32_t step_bytes =
        (header[0x1cu / 4u] * header[0x20u / 4u]) / 1000u * 2u;
    for (unsigned step = 0; step < 3u; ++step) {
        gx8002_image_b_imcra_process_10015d34(
            mode_state[0x0cu / 4u], output, output);
        output += step_bytes;
    }
}
