/* Native convert_pb_to_internal 0x595f4c..0x596093. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *codec_allocate(uint32_t);
extern void audio_file_heap_free(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

typedef struct TagNode {
    uint8_t kind;
    uint8_t reserved[3];
    char *text;
    char *extended;
    uint16_t text_length;
    uint16_t extended_length;
    uint32_t metadata;
    struct TagNode *prev;
    struct TagNode *next;
} TagNode;

_Static_assert(sizeof(TagNode) == 28, "tag node layout");
_Static_assert(__builtin_offsetof(TagNode, text_length) == 12, "tag text length offset");
_Static_assert(__builtin_offsetof(TagNode, metadata) == 16, "tag metadata offset");

static const char module[] = "conversate.tag";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "convert_pb_to_internal";
static const char text_failed[] =
    "Failed to allocate memory for tag_text, size: %d";
static const char text_failed_short[] =
    "[conversate.tag]Failed to allocate memory for tag_text, size: %d";
static const char extended_failed[] =
    "Failed to allocate memory for tag_text_extend, size: %d";
static const char extended_failed_short[] =
    "[conversate.tag]Failed to allocate memory for tag_text_extend, size: %d";

uint32_t audio_conversate_tag_node_from_pb_595f4c(const void *input,
                                                     void *output) {
    const uint8_t *const pb = (const uint8_t *)input;
    TagNode *const node = (TagNode *)output;
    audio_uart_buffer_zero(node, 20u, 0u);
    node->kind = pb[0];
    node->metadata = (uint32_t)pb[0x488] |
        ((uint32_t)pb[0x489] << 8) |
        ((uint32_t)pb[0x48a] << 16) |
        ((uint32_t)pb[0x48b] << 24);
    const uint16_t length = (uint16_t)((uint16_t)pb[2] |
                                        ((uint16_t)pb[3] << 8));
    if (length != 0u) {
        node->text_length = length;
        node->text = (char *)codec_allocate((uint32_t)length + 1u);
        if (!node->text) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module, path, function, 36u,
                                   text_failed, (uint32_t)length + 1u);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                audio_log_simple(0x04400000u, text_failed_short,
                                 text_failed_short, (uint32_t)length + 1u);
            return 0u;
        }
        (void)audio_queue_copy_bytes(node->text, pb + 4, length);
        node->text[length] = 0;
    } else {
        node->text = (char *)0;
        node->text_length = 0u;
    }
    const uint16_t extended_length = (uint16_t)((uint16_t)pb[0x84] |
                                                 ((uint16_t)pb[0x85] << 8));
    if (extended_length != 0u) {
        node->extended_length = extended_length;
        node->extended = (char *)codec_allocate((uint32_t)extended_length + 1u);
        if (!node->extended) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module, path, function, 52u,
                                   extended_failed,
                                   (uint32_t)extended_length + 1u);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                audio_log_simple(0x04400000u, extended_failed_short,
                                 extended_failed_short,
                                 (uint32_t)extended_length + 1u);
            if (node->text) {
                audio_file_heap_free(node->text);
                node->text = (char *)0;
            }
            return 0u;
        }
        (void)audio_queue_copy_bytes(node->extended, pb + 0x86, extended_length);
        node->extended[extended_length] = 0;
    } else {
        node->extended = (char *)0;
        node->extended_length = 0u;
    }
    return 1u;
}
