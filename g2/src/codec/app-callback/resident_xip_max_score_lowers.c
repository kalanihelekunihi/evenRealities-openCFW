/* SPDX-License-Identifier: MIT
 * Native XIP 0x10208980, 0x10208b58 and 0x10208b68, matched to pinned
 * NationalChip kws_strategy.c. Activation entries are 20 bytes; source
 * allocation and placement for the live SRAM states remain linker work.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
struct gx8002_keyword_list {
    uint32_t count;
    const void *parameters;
};
extern const struct gx8002_keyword_list *
gx8002_resident_keyword_list_get_264dc(void);

struct gx8002_activation_entry {
    int32_t kws_index;
    int32_t kws_value;
    float kws_score;
    int32_t score_index;
    void *priv;
};
_Static_assert(sizeof(struct gx8002_activation_entry) == 20,
               "native activation entry stride");

struct gx8002_activation_state {
    int32_t total;
    struct gx8002_activation_entry entries[8];
};
_Static_assert(sizeof(struct gx8002_activation_state) == 164,
               "native activation state extent");

void gx8002_xip_kws_insert_activation_10208980(
    int index, int value, float score, int score_index, void *priv)
{
    struct gx8002_activation_state *const state =
        (struct gx8002_activation_state *)(uintptr_t)UINT32_C(0x2002e7a8);
    for (int32_t existing = 0; existing < state->total; ++existing) {
        struct gx8002_activation_entry *const entry =
            &state->entries[existing];
        if (entry->kws_value == value && entry->kws_index == index) {
            if (score > entry->kws_score) entry->kws_score = score;
            return;
        }
    }
    if (state->total >= 8) {
        (void)gx8002_xip_tws_publish_10206c24(
            "[ST]==ERROR== Array [activation_kws] overflow\n");
        return;
    }
    struct gx8002_activation_entry *const entry =
        &state->entries[state->total];
    entry->kws_index = index;
    entry->kws_value = value;
    entry->kws_score = score;
    entry->score_index = score_index;
    entry->priv = priv;
    ++state->total;
}

float gx8002_xip_bunkws_offset_10208b58(void *context, float threshold)
{
    (void)context;
    (void)threshold;
    volatile const float *const offset =
        (volatile const float *)(uintptr_t)UINT32_C(0x2002e850);
    return *offset;
}

void gx8002_xip_bunkws_offset_clear_10208b68(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e84c);
    state[3] = 0u;
    state[1] = 0u;
}

int gx8002_xip_bionic_run_10208b78(void *raw_context,
                                    void *parameter, float score,
                                    float threshold, float *window)
{
    (void)parameter;
    (void)score;
    (void)threshold;
    (void)window;
    const uint8_t *const context = raw_context;
    const uint8_t *const header = (const uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)context;
    const uint32_t frame_length =
        *(const uint32_t *)(const void *)(header + 0x1cu);
    const uint32_t frame_count =
        *(const uint32_t *)(const void *)(header + 0x24u);
    const struct gx8002_keyword_list *const keywords =
        gx8002_resident_keyword_list_get_264dc();
    const uint32_t timeout =
        (keywords->count * UINT32_C(1000000)) >> 2u;
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e84c);
    volatile uint32_t *const counter =
        (volatile uint32_t *)(void *)(state + 0x0cu);
    volatile float *const offset =
        (volatile float *)(void *)(state + 4u);
    uint32_t ticks = *counter + 1u;
    *counter = ticks;
    if ((int32_t)timeout <
            (int32_t)(ticks * frame_count * frame_length) &&
        *offset < 150.0f) {
        *counter = 0u;
        const float next = *offset + 5.0f;
        *offset = next > 150.0f ? 150.0f : next;
        (void)gx8002_xip_tws_publish_10206c24(
            "[ST]bunkws threshold_offset: %d\n", (int32_t)*offset);
    }
    return 0;
}
