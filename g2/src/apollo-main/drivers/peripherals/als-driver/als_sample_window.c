/* ALS sample windows, stock driver\sensor\als\als.c.
 * Native 0x4ada02..0x4adb9a and 0x4adc84..0x4adcd8.
 *
 * Two ring buffers of readings:
 *  - a 5-sample peak window (index 0x200741c8, count 0x200741cc, words at
 *    0x20073c98) whose maximum is the filtered reading used for the target and
 *    whose spread unlocks a manual-brightness lock;
 *  - a 20-sample dark window (index 0x200741d0, count 0x200741d4, words at
 *    0x20072948) that detects extreme darkness.
 * Each push advances the index first, so the newest sample is at the index.
 * The counts saturate only by wrapping; they are cleared on open. */
#include <stdbool.h>
#include <stdint.h>
#include "g2_als.h"

#define PEAK_WINDOW 5u
#define DARK_WINDOW 20u
#define DARK_SAMPLE_LIMIT 3u  /* a sample below this counts as dark */
#define DARK_SAMPLE_QUORUM 19u
#define PEAK_SPREAD_LIMIT 300u

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */

static uint32_t *peak_window(void)
{
    return (uint32_t *)(void *)audio_als_manual_window;
}

/* Push a reading into the 5-sample peak window. */
void als_function_04(uint32_t lux)
{
    audio_als_manual_sample = (audio_als_manual_sample + 1u) % PEAK_WINDOW;
    peak_window()[audio_als_manual_sample] = lux;
    ++audio_als_manual_accumulator;
}

/* Push a reading into the 20-sample dark window. */
void als_function_05(uint32_t lux)
{
    g2_als_dark_window_index = (g2_als_dark_window_index + 1u) % DARK_WINDOW;
    g2_als_dark_window[g2_als_dark_window_index] = lux;
    ++g2_als_dark_window_count;
}

void als_function_06(void)
{
    g2_als_dark_window_count = 0u;
    g2_als_dark_window_index = 0u;
    audio_uart_buffer_zero(g2_als_dark_window, sizeof g2_als_dark_window, 0u);
}

/* True once the dark window is full and at least 19 of 20 samples are < 3. */
bool als_function_07(void)
{
    uint32_t dark = 0u;
    if (g2_als_dark_window_count < DARK_WINDOW)
        return false;
    for (uint32_t i = 0u; i < DARK_WINDOW; i++)
        if (g2_als_dark_window[i] < DARK_SAMPLE_LIMIT)
            ++dark;
    return dark >= DARK_SAMPLE_QUORUM;
}

uint32_t als_function_09(void)
{
    return peak_window()[audio_als_manual_sample];
}

/* Maximum of the peak window; the newest sample until it has filled. */
uint32_t als_function_10(void)
{
    const uint32_t *window = peak_window();
    if (audio_als_manual_accumulator < PEAK_WINDOW)
        return window[audio_als_manual_sample];
    uint32_t peak = 0u;
    for (uint32_t i = 0u; i < PEAK_WINDOW; i++)
        if (window[i] >= peak)
            peak = window[i];
    return peak;
}

/* True when the full peak window spans more than 300 (max - min). */
bool als_function_12(void)
{
    const uint32_t *window = peak_window();
    if (audio_als_manual_accumulator < PEAK_WINDOW)
        return false;
    uint32_t high = window[0];
    uint32_t low = window[0];
    for (uint32_t i = 1u; i < PEAK_WINDOW; i++) {
        if (window[i] >= high)
            high = window[i];
        if (window[i] <= low)
            low = window[i];
    }
    return high - low > PEAK_SPREAD_LIMIT;
}
