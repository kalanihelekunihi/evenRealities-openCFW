/* Private layouts shared by the a-29 reconstruction of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\ui_even_ai.c
 * (ui_even_ai_stream.c and ui_even_ai_dialog.c in this directory). */
#ifndef G2_UI_EVEN_AI_INTERNAL_H
#define G2_UI_EVEN_AI_INTERNAL_H

#include <stdint.h>
#include <stddef.h>

/* One question/answer dialog. Five of these live in a static pool (RAM table
 * used by even_ai_create_dialog_node 0x4e6956, stride 0x24, +0x1c in-use). */
typedef struct g2_even_ai_dialog_node {
    void *question_label;                /* +0x00 lv_label */
    void *answer_obj;                    /* +0x04 answer container */
    void *answer_label;                  /* +0x08 lv_label streamed into */
    void *answer_extra0;                 /* +0x0c */
    void *answer_extra1;                 /* +0x10 */
    uint8_t grayed;                      /* +0x14 question shown grayed */
    uint8_t pad15[3];
    uint16_t question_chars;             /* +0x18 */
    uint16_t answer_chars;               /* +0x1a */
    uint8_t in_use;                      /* +0x1c pool slot busy */
    uint8_t pad1d[3];
    struct g2_even_ai_dialog_node *next; /* +0x20 */
} g2_even_ai_dialog_node_t;
_Static_assert(sizeof(g2_even_ai_dialog_node_t) == 0x24u, "dialog node pool stride");

/* Dialog list at RAM 0x200739fc (directly followed by the stream state). */
typedef struct {
    uint32_t word0;                      /* +0x00 */
    uint32_t word4;                      /* +0x04 */
    void *dialog_cont;                   /* +0x08 scrollable dialog container */
    void *label_listening;               /* +0x0c */
    g2_even_ai_dialog_node_t *head;      /* +0x10 oldest dialog */
    g2_even_ai_dialog_node_t *tail;      /* +0x14 newest dialog */
    uint8_t count;                       /* +0x18 dialog_count, at most 5 */
    uint8_t pad19;
    uint16_t total_chars;                /* +0x1a */
    uint16_t question_chars;             /* +0x1c */
    uint16_t answer_chars;               /* +0x1e */
} g2_even_ai_dialogs_t;
_Static_assert(sizeof(g2_even_ai_dialogs_t) == 0x20u, "dialog list");

/* Streaming display state at RAM 0x20073a1c (returned by
 * even_ai_text_stream_service_get). */
typedef struct {
    uint8_t phase;                       /* +0x00 0 idle, 1 streaming, 2 answer finished */
    uint8_t kind;                        /* +0x01 1 question, 2 answer */
    uint16_t start_len;                  /* +0x02 */
    uint16_t shown_len;                  /* +0x04 */
    uint16_t step_count;                 /* +0x06 char_count in the sync log */
    uint16_t chunk_size;                 /* +0x08 steps between peer syncs (6) */
    uint8_t pad0a[2];
    uint32_t last_tick;                  /* +0x0c */
    uint32_t interval;                   /* +0x10 ms per step */
    uint8_t wait_sync;                   /* +0x14 */
    uint8_t pad15[3];
    uint32_t wait_tick;                  /* +0x18 */
    uint32_t finish_tick;                /* +0x1c */
} g2_even_ai_stream_state_t;
_Static_assert(sizeof(g2_even_ai_stream_state_t) == 0x20u, "stream state");

/* Height cache at RAM 0x20073f04 for the newest dialog. */
typedef struct {
    uint8_t valid;                       /* +0x00 */
    uint8_t count;                       /* +0x01 dialog count when cached */
    uint8_t pad02[2];
    int32_t question_height;             /* +0x04 */
    int32_t answer_height;               /* +0x08 */
    uint8_t has_question;                /* +0x0c */
    uint8_t has_answer;                  /* +0x0d */
    uint8_t pad0e[2];
} g2_even_ai_layout_cache_t;
_Static_assert(sizeof(g2_even_ai_layout_cache_t) == 0x10u, "layout cache");

#define EVEN_AI_CHAR_WINDOW 0x400u       /* chars kept before old dialogs are dropped */
#define EVEN_AI_SYNC_APP 7u              /* sync interface app id */

extern g2_even_ai_dialogs_t g2_even_ai_dialogs;             /* RAM 0x200739fc */
extern uint8_t audio_even_ai_stream_display_state_20073a1c[0x20]; /* RAM 0x20073a1c */
extern g2_even_ai_layout_cache_t g2_even_ai_layout_cache;   /* RAM 0x20073f04 */
extern uint8_t g2_even_ai_anim_busy;                        /* RAM 0x2007503a */
extern void *g2_even_ai_event_fifo;                         /* RAM 0x20074c00 */

/* ui_even_ai.c functions used across the two files. */
void even_ai_style_apply(void *obj, int32_t value, uint32_t selector);
uint32_t even_ai_tick_get(void);
void even_ai_layout_refresh(void);
uint32_t even_ai_scroll_needed(void);
void even_ai_scroll_to(void *obj, int32_t y, uint32_t anim_time);
void even_ai_scroll_by_delta(int32_t direction, int32_t delta, int32_t speed);
void even_ai_layout_cache_invalidate(void);
void even_ai_node_stream_state_init(g2_even_ai_dialog_node_t *node, uint8_t question,
                                    uint16_t chars);
void even_ai_manage_char_window(void);

/* Shared stock callees. */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);    /* lv_obj_is_valid */
extern void audio_lv_label_text_49942e(void *label, const char *text); /* lv_label_set_text */
extern uint32_t audio_log_flags(void);                                  /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                     /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#endif
