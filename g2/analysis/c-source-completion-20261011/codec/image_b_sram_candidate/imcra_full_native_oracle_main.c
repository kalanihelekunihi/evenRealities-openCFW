#include <stdint.h>

static uint32_t state[0xc4u / 4u + 1u];
static int16_t history[16], input[8], window[16], work[512];
static int16_t spectrum[514], residual[16], output_window[8], output[8];
static float energy[4], gain[4], smooth_a[4], smooth_b[4];
static float prior_a[4], prior_b[4], history_a[4], history_b[4];
static float adaptive[4], noise[4], scaled[4], previous[4], scratch[4];
static float weighted[4], flags[4], gain_table[4], ring_a[8], ring_b[8];
static float weights[3];
static int16_t residual_before[8];

static uint32_t bits(float value)
{
    union { float f; uint32_t u; } word = {.f = value};
    return word.u;
}

static void copy_loaded_data(void)
{
    const volatile uint8_t *source =
        (const volatile uint8_t *)(uintptr_t)0x10016f60u;
    volatile uint8_t *target =
        (volatile uint8_t *)(uintptr_t)0x20016f60u;
    for (uint32_t i = 0; i < 300u; ++i)
        target[i] = source[i];
}

#ifdef SOURCE_MODE
extern void gx8002_image_b_imcra_process_10015d34(
    uint8_t *, const int16_t *, int16_t *);
#endif

int main(void)
{
    copy_loaded_data();
    for (uint32_t i = 0; i < 16u; ++i) {
#if defined(SIGNAL_CASE) && SIGNAL_CASE == 2
        history[i] = (int16_t)((i & 1u) ? 24000 : -23000);
        window[i] = (int16_t)((i & 1u) ? 24576 : 28000);
#else
        history[i] = (int16_t)(i * 113u - 800u);
        window[i] = 16384;
#endif
    }
    for (uint32_t i = 0; i < 8u; ++i) {
#if defined(SIGNAL_CASE) && SIGNAL_CASE == 2
        input[i] = (int16_t)((i & 1u) ? -27000 : 26000);
        output_window[i] = 30000;
#else
        input[i] = (int16_t)(i * 79u - 210u);
        output_window[i] = 16384;
#endif
    }
    weights[0] = 0.25f;
    weights[1] = 0.5f;
    weights[2] = 0.25f;
    state[0x0cu/4u] = 16u;
    state[0x10u/4u] = 512u;
    state[0x14u/4u] = 8u;
    state[0x18u/4u] = 512u;
    state[0x1cu/4u] = 4u;
    state[0x20u/4u] = 0u;
    state[0x24u/4u] = (uint32_t)(uintptr_t)history;
    state[0x2cu/4u] = (uint32_t)(uintptr_t)residual;
    state[0x30u/4u] = (uint32_t)(uintptr_t)window;
    state[0x34u/4u] = (uint32_t)(uintptr_t)output_window;
    state[0x38u/4u] = (uint32_t)(uintptr_t)work;
    state[0x3cu/4u] = (uint32_t)(uintptr_t)spectrum;
    state[0x40u/4u] = (uint32_t)(uintptr_t)energy;
    state[0x44u/4u] = (uint32_t)(uintptr_t)gain;
    state[0x48u/4u] = bits(0.5f);
    state[0x4cu/4u] = bits(1.0f);
    state[0x50u/4u] = bits(1.2f);
    state[0x54u/4u] = bits(2.0f);
    state[0x58u/4u] = bits(0.5f);
    state[0x5cu/4u] = bits(0.5f);
    state[0x60u/4u] = bits(0.5f);
    state[0x64u/4u] = bits(1.0f);
    state[0x6cu/4u] = 2u;
    state[0x70u/4u] = 2u;
    state[0x74u/4u] = 1u;
    state[0x78u/4u] = (uint32_t)(uintptr_t)smooth_a;
    state[0x7cu/4u] = (uint32_t)(uintptr_t)smooth_b;
    state[0x80u/4u] = (uint32_t)(uintptr_t)prior_a;
    state[0x84u/4u] = (uint32_t)(uintptr_t)prior_b;
    state[0x88u/4u] = (uint32_t)(uintptr_t)ring_a;
    state[0x8cu/4u] = (uint32_t)(uintptr_t)history_a;
    state[0x90u/4u] = (uint32_t)(uintptr_t)ring_b;
    state[0x94u/4u] = (uint32_t)(uintptr_t)history_b;
    state[0x98u/4u] = (uint32_t)(uintptr_t)previous;
    state[0x9cu/4u] = (uint32_t)(uintptr_t)adaptive;
    state[0xa0u/4u] = (uint32_t)(uintptr_t)noise;
    state[0xa4u/4u] = (uint32_t)(uintptr_t)scaled;
    state[0xa8u/4u] = (uint32_t)(uintptr_t)scratch;
    state[0xacu/4u] = (uint32_t)(uintptr_t)weights;
    state[0xb0u/4u] = (uint32_t)(uintptr_t)weighted;
    state[0xb4u/4u] = (uint32_t)(uintptr_t)flags;
    state[0xb8u/4u] = (uint32_t)(uintptr_t)gain_table;
    state[0xbcu/4u] =
#ifdef CASE_MODE
        CASE_MODE;
#else
        2u;
#endif
    state[0xc0u/4u] = bits(0.1f);
    for (uint32_t frame = 0;
         frame < (uint32_t)(
#ifdef FRAMES
             FRAMES
#else
             1
#endif
         ); ++frame) {
        for (uint32_t i = 0; i < 8u; ++i)
            residual_before[i] = residual[i];
#ifdef SOURCE_MODE
        gx8002_image_b_imcra_process_10015d34(
            (uint8_t *)(void *)state, input, output);
#else
        ((void (*)(uint32_t *, int16_t *, int16_t *))(uintptr_t)0x10015d34u)(
            state, input, output);
#endif
    }
    volatile uint32_t *trace = (volatile uint32_t *)(uintptr_t)0xffffc040u;
    *trace = state[0x20u/4u];
    for (uint32_t i = 0; i < 8u; ++i)
        *trace = (uint16_t)output[i];
    for (uint32_t i = 0; i < 4u; ++i)
        *trace = bits(energy[i]);
    for (uint32_t i = 0; i < 4u; ++i)
        *trace = bits(gain_table[i]);
    for (uint32_t i = 0; i < 4u; ++i)
        *trace = bits(gain[i]);
    for (uint32_t i = 0; i < 4u; ++i)
        *trace = bits(adaptive[i]);
    for (uint32_t i = 0; i < 16u; ++i)
        *trace = (uint16_t)spectrum[i];
    for (uint32_t i = 0; i < 16u; ++i)
        *trace = (uint16_t)work[i];
    for (uint32_t i = 0; i < 8u; ++i)
        *trace = (uint16_t)residual[i];
    for (uint32_t i = 0; i < 8u; ++i)
        *trace = (uint16_t)residual_before[i];
    for (uint32_t i = 0; i < 8u; ++i)
        *trace = (uint16_t)window[i];
    for (uint32_t i = 0; i < 8u; ++i)
        *trace = (uint16_t)output_window[i];
    return 0;
}
