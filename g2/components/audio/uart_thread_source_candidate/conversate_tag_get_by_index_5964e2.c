/* Native conversate_tag_get_data_by_index, 0x5964e2..0x59674d. */
#include <stdint.h>

typedef struct TagNode {
    uint32_t kind;
    const char *text;
    uint8_t payload[12];
    struct TagNode *prev;
    struct TagNode *next;
} TagNode;
_Static_assert(sizeof(TagNode) == 28u, "Conversate tag node ABI");

extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern uint32_t g2_log_module_length(const char *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.tag";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_get_data_by_index";
static const char no_storage[] = "Storage not initialized";
static const char no_storage_short[] =
    "[conversate.tag]Storage not initialized";
static const char out_of_range[] = "Index %d >= count %d";
static const char out_of_range_short[] =
    "[conversate.tag]Index %d >= count %d";
static const char circular[] = "Circular list traversal error at index %d";
static const char circular_short[] =
    "[conversate.tag]Circular list traversal error at index %d";
static const char missing[] = "Failed to find node at index %d";
static const char missing_short[] =
    "[conversate.tag]Failed to find node at index %d";
static const char bad_type[] = "Invalid tag type: %d";
static const char bad_type_short[] =
    "[conversate.tag]Invalid tag type: %d";
static const char bad_text[] = "Invalid tag text: %s";
static const char bad_text_short[] =
    "[conversate.tag]Invalid tag text: %s";
static const char null_text[] = "NULL";

static uint32_t word(const uint8_t *p, uint32_t offset) {
    return *(const uint32_t *)(const void *)(p + offset);
}
static uint16_t half(const uint8_t *p, uint32_t offset) {
    return *(const uint16_t *)(const void *)(p + offset);
}

static void note_simple(uint32_t level, uint32_t line, uint32_t compact,
                        const char *message, const char *short_message) {
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(compact, short_message, short_message);
}
static void note_number(uint32_t level, uint32_t line, uint32_t compact,
                        const char *message, const char *short_message,
                        uint32_t value) {
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, function, line, message, value);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(compact, short_message, short_message, value);
}

TagNode *audio_conversate_tag_get_by_index_5964e2(uint32_t index) {
    const uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] == 0u) {
        note_simple(1u, 0x105u, 0x04000000u, no_storage,
                    no_storage_short);
        return 0;
    }
    const uint16_t selected = (uint16_t)index;
    const uint16_t count = half(state, 8u);
    if (selected >= count) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, source, function, 0x10bu,
                               out_of_range, selected, count);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10800000u,
                                        out_of_range_short,
                                        out_of_range_short, selected, count);
        return 0;
    }
    TagNode *node = (TagNode *)(uintptr_t)word(state, 0u);
    const TagNode *const head = node;
    uint32_t position = 0u;
    while ((uint16_t)position < selected && node != 0) {
        node = node->prev;
        if (node == head && (uint16_t)position + 1u < selected) {
            note_number(1u, 0x115u, 0x04400000u, circular,
                        circular_short, (uint16_t)position + 1u);
            return 0;
        }
        ++position;
    }
    if (node == 0) {
        note_number(1u, 0x11bu, 0x04400000u, missing,
                    missing_short, selected);
        return 0;
    }
    const uint8_t type = (uint8_t)node->kind;
    if (type == 0u || type >= 5u) {
        note_number(1u, 0x120u, 0x04400000u, bad_type,
                    bad_type_short, type);
        return 0;
    }
    if (node->text == 0 || g2_log_module_length(node->text) == 0u) {
        const char *const text = node->text ? node->text : null_text;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x125u,
                               bad_text, text);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u,
                                        bad_text_short, bad_text_short, text);
        return 0;
    }
    return node;
}
