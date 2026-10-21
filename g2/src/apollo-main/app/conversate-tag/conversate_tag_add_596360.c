/* Native conversate_tag_add 0x596360..0x5964e1. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];

typedef struct TagNode {
    uint32_t kind;
    const char *text;
    uint8_t payload[12];
    struct TagNode *prev;
    struct TagNode *next;
} TagNode;

extern TagNode *audio_conversate_tag_node_create_5960c2(const void *);

static const char module[] = "conversate.tag";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_add";
static const char null_message[] = "Tag data is NULL";
static const char null_short[] = "[conversate.tag]Tag data is NULL";
static const char uninitialized[] = "Storage not initialized";
static const char uninitialized_short[] = "[conversate.tag]Storage not initialized";
static const char allocation_failed[] = "Failed to create new tag node";
static const char allocation_failed_short[] =
    "[conversate.tag]Failed to create new tag node";
static const char null_text[] = "NULL";
static const char added[] = "Added tag(text: %s) at head, total count: %d";
static const char added_short[] =
    "[conversate.tag]Added tag(text: %s) at head, total count: %d";

uint32_t audio_conversate_store_tag_596360(const void *tag) {
    if (!tag) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 211u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return 0u;
    }
    uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 216u, uninitialized);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, uninitialized_short, uninitialized_short);
        return 0u;
    }
    TagNode *const node = audio_conversate_tag_node_create_5960c2(tag);
    if (!node) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 223u,
                               allocation_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, allocation_failed_short,
                             allocation_failed_short);
        return 0u;
    }
    TagNode **const head_cell = (TagNode **)(void *)state;
    TagNode *const head = *head_cell;
    if (!head) {
        node->prev = node;
        node->next = node;
    } else {
        TagNode *const tail = head->next;
        node->prev = head;
        node->next = tail;
        head->next = node;
        tail->prev = node;
    }
    *head_cell = node;
    const uint16_t count = (uint16_t)((uint16_t)state[8] |
                                      ((uint16_t)state[9] << 8)) + 1u;
    state[8] = (uint8_t)count;
    state[9] = (uint8_t)(count >> 8);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 247u, added,
                           node->text ? node->text : null_text, count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10800000u, added_short, added_short,
                         node->text ? node->text : null_text, count);
    return 1u;
}
