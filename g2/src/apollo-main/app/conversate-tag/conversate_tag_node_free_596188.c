#include <stdint.h>

/* Stock Apollo Main 0x596094..0x5960c1 and 0x596188..0x59619d. */
extern void audio_file_heap_free(void *);

void audio_conversate_tag_node_destruct_596094(void *node)
{
    uint8_t *base = (uint8_t *)node;
    void *text = *(void **)(void *)(base + 4u);
    if (text != 0) {
        audio_file_heap_free(text);
        *(void **)(void *)(base + 4u) = 0;
        *(uint16_t *)(void *)(base + 12u) = 0;
    }
    void *secondary = *(void **)(void *)(base + 8u);
    if (secondary != 0) {
        audio_file_heap_free(secondary);
        *(void **)(void *)(base + 8u) = 0;
        *(uint16_t *)(void *)(base + 14u) = 0;
    }
}

void audio_conversate_tag_node_free_596188(void *node)
{
    if (node != 0) {
        audio_conversate_tag_node_destruct_596094(node);
        audio_file_heap_free(node);
    }
}
