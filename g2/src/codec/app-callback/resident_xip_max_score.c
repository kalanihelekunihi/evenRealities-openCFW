/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102086dc..0x10208875, reconstructed against pinned
 * NationalChip lvp/vui/kws/max_decoder.c and lvp_param.h. The stock product
 * fixes the window length at ten and activation count at one. Lower strategy
 * functions remain real imported C contracts until their own bodies are
 * reconstructed. Native FPU instruction constants are 1000.0f and 10.0f.
 */
#include <stdint.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern void gx8002_resident_cache_invalidate_25608(void *, int32_t);
extern int gx8002_xip_bionic_run_10208b78(void *context,
                                          void *parameter, float score,
                                          float threshold, float *window);
extern float gx8002_xip_bunkws_offset_10208b58(void *context,
                                                float threshold);
extern void gx8002_xip_bunkws_offset_clear_10208b68(void);
extern void gx8002_xip_kws_insert_activation_10208980(
    int index, int value, float score, int score_index, void *priv);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

static uint32_t max_load32(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}

static void max_store32(volatile uint8_t *base, uint32_t offset,
                        uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

uint32_t gx8002_xip_max_score_102086dc(void *raw_context, uint32_t major)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e744);
    volatile uint8_t *const context = raw_context;
    gx8002_xip_memset_102099cc((void *)state, 0u, 2u);
    void *const snpu_buffer =
        (void *)(uintptr_t)max_load32(context, 0x10u);
    const volatile uint8_t *const header =
        (volatile const uint8_t *)(uintptr_t)max_load32(context, 0u);
    gx8002_resident_cache_invalidate_25608(
        snpu_buffer, (int32_t)max_load32(header, 0x44u));
    const volatile float *const output =
        (volatile const float *)((const uint8_t *)snpu_buffer + 0x2110u);
    const uint32_t window_index =
        (uint32_t)((int32_t)max_load32(state, 4u) % 10);
    context[0x0du] = 0u;
    const uint32_t count = max_load32(state, 0x58u);
    for (uint32_t index = 0u; index < count; ++index) {
        volatile uint8_t *const entry = (volatile uint8_t *)(uintptr_t)
            (max_load32(state, 0x5cu) + index * 0x58u);
        const uint32_t entry_major = max_load32(entry, 0x54u);
        if ((entry_major & 1u) != major) continue;
        const int32_t score = (int32_t)(output[index] * 1000.0f);
        const int32_t base_threshold = (int32_t)max_load32(entry, 0x4cu);
        (void)gx8002_xip_bionic_run_10208b78(
            raw_context, (void *)entry, (float)score,
            (float)base_threshold, (float *)0);
        int32_t threshold = base_threshold;
        if (entry_major != 0u)
            threshold = (int32_t)((float)base_threshold +
                gx8002_xip_bunkws_offset_10208b58(
                    raw_context, (float)base_threshold));
        volatile uint32_t *const cell =
            (volatile uint32_t *)(void *)(state + 8u + window_index * 8u +
                                         index * 4u);
        if (score > threshold && (entry_major & 1u) == major) {
            max_store32(state, 0x60u, (uint32_t)score);
            *cell = 1u;
            uint8_t active = state[index];
            for (uint32_t row = 0u; row < 10u; ++row)
                active = (uint8_t)(active + max_load32(
                    state, 8u + row * 8u + index * 4u));
            state[index] = active;
            if (active == 1u) {
                gx8002_xip_kws_insert_activation_10208980(
                    (int)index, (int)max_load32(entry, 0x50u),
                    (float)score / 10.0f, 0, (void *)0);
                const int32_t peak = (int32_t)max_load32(state, 0x60u);
                (void)gx8002_xip_tws_publish_10206c24(
                    "[LVP_MAX_DECODE]awaken ctx:%d,Kws:%s[%d],th:%d,S:%d,%d\n",
                    (int32_t)max_load32(context, 8u), (const char *)entry,
                    (int32_t)max_load32(entry, 0x50u), threshold, peak,
                    peak - threshold);
                max_store32(state, 0x60u, 0u);
                if (entry_major != 0u)
                    gx8002_xip_bunkws_offset_clear_10208b68();
            }
        } else {
            *cell = 0u;
        }
    }
    return 0u;
}
