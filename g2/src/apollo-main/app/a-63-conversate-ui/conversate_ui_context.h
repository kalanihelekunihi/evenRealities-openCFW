/* Conversate UI context at RAM 0x20071368 (0xac bytes), as seen by the stock
 * conversate_ui_main_page.c, conversate_ui_menu_page.c, conversate_ui_tag_page.c
 * and conversate_ui_prep_note_page.c units. Storage is owned elsewhere:
 * byte 0 by conversate_ui_state_ram_20071368.c, +0x01..+0x94 by
 * audio_conversate_ui_settings_extension_20071369 and +0x95..+0xab by
 * audio_conversate_ui_deinit_tail_200713fd; the units here address the whole
 * record through the extension symbol minus one, as the neighbouring units do. */
#ifndef G2_A63_CONVERSATE_UI_CONTEXT_H
#define G2_A63_CONVERSATE_UI_CONTEXT_H

#include <stdint.h>

typedef struct {
    uint32_t tag_id;      /* +0x0 TagNode +0x10 */
    uint8_t open_type;    /* +0x4 1 = auto-popped tag, 0 = opened from the list */
    uint8_t close_type;   /* +0x5 1 when the to-main route value is 2 */
    uint8_t pad[2];
    uint32_t duration_ms; /* +0x8 tick at show, elapsed ms when sent */
} g2_conversate_tag_tracking_t;
_Static_assert(sizeof(g2_conversate_tag_tracking_t) == 12u, "tracking record");

typedef struct {
    uint8_t state;              /* +0x00 page state (2 main list, 4 tag page ...) */
    uint8_t pad01[7];
    void *main_root;            /* +0x08 main page container, faded behind overlays */
    uint8_t pad0c[0x10];
    void *overlay_root;         /* +0x1c tag / prep-note overlay */
    void *title_row;            /* +0x20 */
    void *prep_content;         /* +0x24 prep-note scroll container */
    void *prep_text;            /* +0x28 prep-note text (created by refresh 0x5b6cd0) */
    void *prep_scrollbar;       /* +0x2c */
    uint8_t prep_cache[0x30];   /* +0x30 */
    uint16_t prep_line;         /* +0x60 */
    uint8_t pad62[2];
    void *list;                 /* +0x64 main list container */
    uint8_t pad68[0x14];
    void *top_button;           /* +0x7c prep-note button above the list */
    void *current_button;       /* +0x80 */
    int32_t current_index;      /* +0x84 -1 = top button */
    void *shrink_button;        /* +0x88 */
    uint8_t ai_cue_display;     /* +0x8c */
    uint8_t pad8d[3];
    int32_t overlay_max_height; /* +0x90 */
    uint8_t auto_close_fixed;   /* +0x94 configured auto-close seconds, 0 = by label */
    uint8_t auto_close_seconds; /* +0x95 */
    uint8_t selected;           /* +0x96 */
    uint8_t pad97;
    uint8_t animating;          /* +0x98 */
    uint8_t pad99[7];
    g2_conversate_tag_tracking_t tracking; /* +0xa0 */
} g2_conversate_ui_t;
_Static_assert(sizeof(g2_conversate_ui_t) == 0xacu, "conversate UI context");

extern uint8_t audio_conversate_ui_settings_extension_20071369[]; /* RAM 0x20071369 */

#define G2_CONVERSATE_UI \
    ((g2_conversate_ui_t *)(void *)((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u))

/* Input codes delivered to the page input handlers. */
enum {
    CONV_INPUT_CLICK = 0x0a,
    CONV_INPUT_SCROLL_UP = 0x44,
    CONV_INPUT_SCROLL_DOWN = 0x45,
    CONV_INPUT_DOUBLE_CLICK = 0x48,
};

/* Scroll input payload: event +0x10 points at {speed, delta}. */
typedef struct {
    uint8_t pad[0x10];
    const int32_t *motion; /* +0x10 [0] speed, [1] delta */
} g2_conversate_input_t;

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Stock two-sink log idiom: full record when flag bit 1 is set, compressed
 * record (id word, key string, format string, args) when bit 0 or 2 is set. */
#define CONV_LOG0(level, fn, line, cflags, full, compact)                                   \
    do {                                                                                    \
        if (audio_log_flags() & 2u)                                                         \
            audio_log_extended((level), LOG_MODULE, LOG_PATH, (fn), (line), (full));       \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                           \
            (void)compress_log_output((cflags), (compact), (compact));                      \
    } while (0)

#define CONV_LOG(level, fn, line, cflags, full, compact, ...)                               \
    do {                                                                                    \
        if (audio_log_flags() & 2u)                                                         \
            audio_log_extended((level), LOG_MODULE, LOG_PATH, (fn), (line), (full),        \
                               __VA_ARGS__);                                                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                           \
            (void)compress_log_output((cflags), (compact), (compact), __VA_ARGS__);         \
    } while (0)

#endif
