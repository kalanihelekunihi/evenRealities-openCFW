/* Private layout shared by the a-67 terminal UI units: the terminal UI state
 * record at RAM 0x2006e0d0 (0x2a0 bytes, declared elsewhere as
 * audio_terminal_ui_state_base) and the cross-unit helper prototypes. */
#ifndef G2_TERMINAL_UI_A67_H
#define G2_TERMINAL_UI_A67_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint8_t reserved_000[0x4];
    void *agent_text;           /* +0x004 agent output scroll container */
    uint8_t reserved_008[0x1ec];
    void *confirm_content;      /* +0x1f4 interrupt-confirm scroll container */
    uint8_t reserved_1f8[0x1c];
    void *query_panel;          /* +0x214 query panel (scrolling) */
    uint8_t reserved_218[0x4];
    void *query_options;        /* +0x21c option list inside the panel */
    uint8_t reserved_220[0x55];
    uint8_t state;              /* +0x275 terminal UI page state */
    uint8_t reserved_276[0x2];
    uint8_t confirm_sel;        /* +0x278 0 = yes, 1 = cancel, 2 = content */
    uint8_t query_idx;          /* +0x279 selected query option */
    int16_t session_idx;        /* +0x27a focused session-list row */
    uint8_t query_browsing;     /* +0x27c 1 = free scrolling above the options */
    uint8_t list_locked;        /* +0x27d */
    uint8_t reserved_27e[0x12];
    uint32_t scroll_tick;       /* +0x290 last accepted throttled scroll */
    uint8_t reserved_294[0x8];
    uint32_t sync_tick;         /* +0x29c session-switch content sync start */
} g2_terminal_ui_t;
_Static_assert(offsetof(g2_terminal_ui_t, confirm_content) == 0x1f4, "terminal ui +0x1f4");
_Static_assert(offsetof(g2_terminal_ui_t, query_panel) == 0x214, "terminal ui +0x214");
_Static_assert(offsetof(g2_terminal_ui_t, query_options) == 0x21c, "terminal ui +0x21c");
_Static_assert(offsetof(g2_terminal_ui_t, state) == 0x275, "terminal ui +0x275");
_Static_assert(offsetof(g2_terminal_ui_t, session_idx) == 0x27a, "terminal ui +0x27a");
_Static_assert(offsetof(g2_terminal_ui_t, scroll_tick) == 0x290, "terminal ui +0x290");
_Static_assert(sizeof(g2_terminal_ui_t) == 0x2a0, "terminal ui state is 0x2a0 bytes");

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* RAM 0x2006e0d0 */
#define G2_TERMINAL_UI ((g2_terminal_ui_t *)(void *)audio_terminal_ui_state_base)

/* Input codes delivered by the input manager. */
#define TERMINAL_KEY_LONG_PRESS 8
#define TERMINAL_KEY_CLICK 10
#define TERMINAL_KEY_SCROLL_UP 0x44
#define TERMINAL_KEY_SCROLL_DOWN 0x45
#define TERMINAL_KEY_DOUBLE_CLICK 0x48
#define TERMINAL_KEY_EXIT 0x4a

/* terminal_query_panel_ui.c (query_panel_align.c). */
uint8_t terminal_ui_query_item_visible_5eb47a(uint8_t idx, int32_t scroll_y);
int32_t terminal_ui_query_first_option_limit_5eb4f6(void);
int32_t terminal_ui_query_panel_get_selected_target_y_5eb646(uint8_t idx, uint8_t keep2);

#endif
