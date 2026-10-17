/* Native create_tag_node 0x5960c2..0x596187. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_conversate_tag_node_from_pb_595f4c(const void *, void *);

typedef struct TagNode {
    uint32_t kind;
    const char *text;
    uint8_t payload[12];
    struct TagNode *prev;
    struct TagNode *next;
} TagNode;

static const char module[] = "conversate.tag";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "create_tag_node";
static const char allocation_failed[] = "Failed to allocate memory for tag node";
static const char allocation_failed_short[] =
    "[conversate.tag]Failed to allocate memory for tag node";
static const char conversion_failed[] =
    "Failed to convert pb data to internal format";
static const char conversion_failed_short[] =
    "[conversate.tag]Failed to convert pb data to internal format";

TagNode *audio_conversate_tag_node_create_5960c2(const void *input) {
    TagNode *const node = (TagNode *)codec_allocate(28u);
    if (!node) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 101u,
                               allocation_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, allocation_failed_short,
                             allocation_failed_short);
        return (TagNode *)0;
    }
    audio_uart_buffer_zero(node, 28u, 0u);
    node->prev = (TagNode *)0;
    node->next = (TagNode *)0;
    if (audio_conversate_tag_node_from_pb_595f4c(input, node) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 112u,
                               conversion_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, conversion_failed_short,
                             conversion_failed_short);
        audio_file_heap_free(node);
        return (TagNode *)0;
    }
    return node;
}
