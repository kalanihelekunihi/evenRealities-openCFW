/* Apollo Main 0x59624e..0x59635f: release the circular tag list. */
#include <stdint.h>

typedef struct TagNode {
    uint32_t kind;
    void *text;
    uint8_t payload[12];
    struct TagNode *prev;
    struct TagNode *next;
} TagNode;
_Static_assert(sizeof(TagNode) == 28u, "Conversate tag node ABI");

extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern void audio_conversate_tag_node_free_596188(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.tag";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c";
static const char function[] = "conversate_tag_storage_deinit";
static const char freeing[] = "Freeing memory for %d tag entries";
static const char freeing_short[] =
    "[conversate.tag]Freeing memory for %d tag entries";
static const char freed[] = "Freed %d tag nodes";
static const char freed_short[] = "[conversate.tag]Freed %d tag nodes";
static const char done[] = "Tag storage deinitialized successfully";
static const char done_short[] =
    "[conversate.tag]Tag storage deinitialized successfully";

static void log_count(uint32_t line, const char *message,
                      const char *compact, uint32_t count)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, source, function, line, message, count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, compact, compact, count);
}

void audio_conversate_ui_exit_child_59624e(void)
{
    uint8_t *const state = audio_conversate_tag_storage_state_200e3af4;
    if (state[10] == 0u) return;
    uint16_t count = *(uint16_t *)(void *)(state + 8u);
    log_count(0xaeu, freeing, freeing_short, count);

    TagNode *node = *(TagNode **)(void *)state;
    if (node != 0) {
        TagNode *tail = node->next;
        tail->prev = 0;
        uint32_t freed_count = 0u;
        do {
            TagNode *const next = node->prev;
            audio_conversate_tag_node_free_596188(node);
            node = next;
            ++freed_count;
        } while (node != 0);
        log_count(0xc0u, freed, freed_short, (uint16_t)freed_count);
    }

    audio_uart_buffer_zero(state, 12u, 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, source, function, 0xc6u, done);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, done_short, done_short);
}
