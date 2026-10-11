/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10208a10..0x10208b45. Control flow and the 10.0f,
 * 0.5f, 0.1f FPU constants are authenticated by native C-SKY disassembly.
 * Algorithm and activation layout follow pinned NationalChip
 * lvp/vui/kws/kws_strategy.c and kws_strategy.h. Keyword table fields are
 * read at their actual native offsets, with the selected SRAM getter.
 */
#include <stdint.h>
#include <stddef.h>

struct gx8002_activation_kws {
    int32_t kws_index;
    int32_t kws_value;
    float kws_score;
    int32_t score_index;
    void *reverse;
};
_Static_assert(sizeof(struct gx8002_activation_kws) == 20,
               "native KWS activation stride");

struct gx8002_activation_list {
    int32_t total;
    struct gx8002_activation_kws entries[8];
};
_Static_assert(sizeof(struct gx8002_activation_list) == 164,
               "native strategy reset extent");

struct gx8002_keyword_list {
    uint32_t count;
    const uint8_t *parameters;
};

extern const struct gx8002_keyword_list *gx8002_resident_keyword_list_get_264dc(void);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

static int32_t gx8002_keyword_s32(const uint8_t *entry, unsigned offset)
{
    return *(const int32_t *)(const void *)(entry + offset);
}

const struct gx8002_activation_kws *gx8002_xip_kws_strategy_10208a10(
    const void *context)
{
    const struct gx8002_activation_list *const list =
        (const struct gx8002_activation_list *)(uintptr_t)UINT32_C(0x2002e7a8);
    if (list->total == 0) return NULL;

    const struct gx8002_activation_kws *selected = &list->entries[0];
    float best_difference = 0.0f;
    for (int32_t index = 0; index < list->total; ++index) {
        const struct gx8002_activation_kws *activation = &list->entries[index];
        const struct gx8002_keyword_list *keywords =
            gx8002_resident_keyword_list_get_264dc();
        const uint8_t *parameter = keywords->parameters +
                                   (uint32_t)activation->kws_index * 0x58u;
        float threshold = (float)gx8002_keyword_s32(parameter, 0x4cu) / 10.0f;
        float difference;
        if (activation->kws_score < threshold) {
            difference = (activation->kws_score - (threshold - 10.0f)) * 0.5f;
            if (difference < 0.0f) difference = 0.1f;
        } else {
            difference = activation->kws_score - threshold;
        }
        if (difference > best_difference) {
            best_difference = difference;
            selected = activation;
        }
        (void)gx8002_xip_tws_publish_10206c24(
            "[ST] Kws:%s[%d],th:%d,S:%d,D:%d\n",
            (const char *)parameter, gx8002_keyword_s32(parameter, 0x50u),
            (int32_t)(10.0f * threshold),
            (int32_t)(10.0f * activation->kws_score),
            (int32_t)(10.0f * difference));
    }

    const struct gx8002_keyword_list *keywords =
        gx8002_resident_keyword_list_get_264dc();
    const uint8_t *parameter = keywords->parameters +
                               (uint32_t)selected->kws_index * 0x58u;
    float threshold = (float)gx8002_keyword_s32(parameter, 0x4cu) / 10.0f;
    uint32_t context_index = *(const uint32_t *)(const void *)(
        (const uint8_t *)context + 8u);
    (void)gx8002_xip_tws_publish_10206c24(
        "[ST] Activation ctx:%d,Kws:%s[%d],th:%d,S:%d\n",
        context_index, (const char *)parameter,
        gx8002_keyword_s32(parameter, 0x50u),
        (int32_t)(10.0f * threshold),
        (int32_t)(10.0f * selected->kws_score));
    return selected;
}
