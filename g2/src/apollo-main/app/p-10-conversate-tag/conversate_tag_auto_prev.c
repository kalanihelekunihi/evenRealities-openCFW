/* conversate_tag_get_data_by_auto_disp_node_prev, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_tag_data.c
 * (module tag "conversate.tag"). Native 0x596930..0x59698f; literals 0x596998,
 * 0x596a88..0x596a8f, 0x596ae4..0x596aef.
 *
 * Steps the auto-pop display cursor one node back along the +0x18 link (named
 * next in the shared TagNode layout of conversate-tag/) and returns it; a NULL cursor restarts at the list head. Returns NULL when auto
 * pop is not active (conversate_tag_auto_pop_check 0x5967bc). */
#include <stdint.h>
#include <stddef.h>

typedef struct TagNode {
    uint32_t kind;          /* +0x00 */
    const char *text;       /* +0x04 */
    uint8_t payload[12];    /* +0x08 */
    struct TagNode *prev;   /* +0x14 */
    struct TagNode *next;   /* +0x18 */
} TagNode;
_Static_assert(sizeof(TagNode) == 28u, "Conversate tag node ABI");

/* RAM 0x200e3af4: list head, auto-display cursor, ... (12 bytes). */
typedef struct {
    TagNode *head;      /* +0x0 */
    TagNode *auto_disp; /* +0x4 */
} g2_conversate_tag_cursor_t;

extern uint8_t audio_conversate_tag_storage_state_200e3af4[12];
extern uint32_t audio_conversate_tag_ai_cue_enabled_5967bc(void);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "conversate.tag"; /* ROM 0x785790 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_tag_data.c"; /* ROM 0x6ec618 */
static const char function_name[] = "conversate_tag_get_data_by_auto_disp_node_prev"; /* ROM 0x732594 */
static const char restart[] = "Auto disp node is NULL, set to head"; /* ROM 0x752d48 */
static const char restart_short[] = "[conversate.tag]Auto disp node is NULL, set to head"; /* ROM 0x727c90 */

TagNode *conversate_tag_get_data_by_auto_disp_node_prev_596930(void)
{
    if (audio_conversate_tag_ai_cue_enabled_5967bc() == 0u)
        return NULL;
    g2_conversate_tag_cursor_t *cursor =
        (g2_conversate_tag_cursor_t *)(void *)audio_conversate_tag_storage_state_200e3af4;
    if (cursor->auto_disp == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module_tag, source_file, function_name, 422u, restart);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x0c000000u, restart_short, restart_short);
        cursor->auto_disp = cursor->head;
    } else {
        cursor->auto_disp = cursor->auto_disp->next;
    }
    return cursor->auto_disp;
}
