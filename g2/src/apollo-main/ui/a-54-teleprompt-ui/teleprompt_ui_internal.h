/* Private layouts of the stock teleprompt page,
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_ui.c.
 * Shared by the a-54 reconstruction (0x555514..0x5573e8); the first half of
 * the same stock file (0x554080..0x555513) is ui/a-53-teleprompt-ui. */
#ifndef G2_TELEPROMPT_UI_INTERNAL_H
#define G2_TELEPROMPT_UI_INTERNAL_H

#include <stdint.h>
#include <stddef.h>

#define TELEPROMPT_WINDOW_PAGES 4u     /* page labels kept in the scroll container */
#define TELEPROMPT_LINE_HEIGHT 28      /* px per text line */
#define TELEPROMPT_PAGE_HEIGHT 0x118   /* 10 lines per page label */
#define TELEPROMPT_APP_ID 6u

/* Page/window state (RAM 0x20073068, also seen by teleprompt_fsm.c). */
typedef struct {
    void *menu_page;            /* +0x00 file-list page */
    void *menu_list;            /* +0x04 button column of the file list */
    void *menu_selected;        /* +0x08 focused file button */
    int32_t menu_index;         /* +0x0c focused index, -1 none */
    void *root;                 /* +0x10 page parent */
    void *title_bar;            /* +0x14 children: 0 time, 1 mode GIF/label, 2 pause icon, 3 pause text */
    void *content;              /* +0x18 scroll container, 4 page labels */
    void *scroll_bar;           /* +0x1c */
    uint8_t state;              /* +0x20 */
    uint8_t busy;               /* +0x21 list scroll or collapse animation running */
    uint8_t reserved_22[2];
    uint32_t start_timestamp;   /* +0x24 RTC seconds at open, cleared on exit */
    uint32_t sync_mode;         /* +0x28 sent with every scroll sync */
    uint32_t window_first_page; /* +0x2c */
    uint32_t current_page;      /* +0x30 */
    uint32_t current_line;      /* +0x34 */
    int32_t last_scroll_y;      /* +0x38 */
    uint32_t switching;         /* +0x3c window switch in progress */
    uint32_t paused;            /* +0x40 */
    uint8_t pause_hint;         /* +0x44 pause icon shown as a hint */
    uint8_t flag_45;            /* +0x45 queued page step (0 none, 1 up, 2 down), cleared on create */
    uint8_t reserved_46[2];
} g2_teleprompt_ui_t;
_Static_assert(offsetof(g2_teleprompt_ui_t, state) == 0x20, "state at +0x20");
_Static_assert(offsetof(g2_teleprompt_ui_t, window_first_page) == 0x2c, "window at +0x2c");
_Static_assert(offsetof(g2_teleprompt_ui_t, paused) == 0x40, "paused at +0x40");
_Static_assert(offsetof(g2_teleprompt_ui_t, flag_45) == 0x45, "flag at +0x45");
_Static_assert(sizeof(g2_teleprompt_ui_t) == 0x48, "stock memset size");

/* Document parameters inside the FSM control block (RAM 0x20109394). */
typedef struct {
    uint8_t mode;               /* +0x00 0 AI, 1 manual ("M"), 2 auto ("A") */
    uint8_t reserved_01[3];
    uint32_t start_page;        /* +0x04 */
    uint32_t start_line;        /* +0x08 */
    uint32_t total_pages;       /* +0x0c */
    uint32_t total_lines;       /* +0x10 */
    int32_t display_width;      /* +0x14 */
    uint8_t reserved_18[0x0c];
    uint32_t display_lines;     /* +0x24 */
} g2_teleprompt_doc_t;
_Static_assert(offsetof(g2_teleprompt_doc_t, display_width) == 0x14, "width at +0x14");
_Static_assert(offsetof(g2_teleprompt_doc_t, display_lines) == 0x24, "lines at +0x24");

/* Teleprompt FSM control block (RAM 0x20109390). */
typedef struct {
    uint8_t reserved_00[4];
    g2_teleprompt_doc_t doc;    /* +0x04 */
    uint8_t scroll_mode;        /* +0x2c 1 = page step, 2 = locked */
    uint8_t reserved_2d[3];
    uint32_t ai_sync[3];        /* +0x30 page, line, char from the last AI sync */
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, ai_sync) == 0x30, "ai_sync at +0x30");

/* File list from the phone (teleprompt_file_list_get). */
typedef struct {
    uint16_t name_len;          /* +0x00 */
    char name[0x42];            /* +0x02 file name sent back on select */
    char title[0x80];           /* +0x44 shown on the button */
} g2_teleprompt_file_item_t;
_Static_assert(sizeof(g2_teleprompt_file_item_t) == 0xc4, "file item is 0xc4 bytes");

typedef struct {
    uint16_t count;             /* +0x00 */
    g2_teleprompt_file_item_t items[]; /* +0x02 */
} g2_teleprompt_file_list_t;

/* APP_PbTxEncodeFileSelect payload (66 bytes). */
typedef struct {
    uint16_t name_len;
    char name[0x40];
} g2_teleprompt_file_select_t;
_Static_assert(sizeof(g2_teleprompt_file_select_t) == 0x42, "file select is 66 bytes");

extern g2_teleprompt_ui_t g2_teleprompt_ui_window;      /* RAM 0x20073068 */
extern g2_teleprompt_fsm_ctrl_t g2_teleprompt_fsm_ctrl; /* RAM 0x20109390 */
extern void *g2_teleprompt_root_20074a7c;               /* RAM 0x20074a7c */

/* Functions reconstructed in teleprompt_ui_actions.c. */
uint32_t teleprompt_ui_visible_lines_5540f0(void);
int32_t teleprompt_ui_title_bar_y_5540f8(uint32_t lines);
void teleprompt_ui_page_label_set_text_555514(void *label, uint32_t page);
void teleprompt_ui_window_labels_refresh_55553c(g2_teleprompt_ui_t *ui, uint32_t first_page);
void *teleprompt_ui_button_create_5555a4(void *parent, const void *icon, const char *text);
uint16_t teleprompt_ui_file_count_555710(void);
void teleprompt_ui_menu_list_event_cb_55571a(void *e);
int32_t teleprompt_ui_action_display_menu_page_555758(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_main_page_create_5558d4(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_display_main_page_555c04(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_file_list_update_555d18(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_file_select_556010(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_page_data_5560d0(uint8_t state, uint32_t page);
int32_t teleprompt_ui_action_menu_scroll_up_556134(uint8_t state, uint32_t count);
int32_t teleprompt_ui_action_menu_scroll_down_556284(uint8_t state, uint32_t count);
int32_t teleprompt_ui_action_main_scroll_up_5563c0(uint8_t state, uint32_t y);
int32_t teleprompt_ui_action_main_scroll_down_556428(uint8_t state, uint32_t y);
int32_t teleprompt_ui_action_ai_sync_5564a8(uint8_t state, uint32_t packed);
int32_t teleprompt_ui_action_scroll_sync_556688(uint8_t state, uint32_t packed);
void *teleprompt_ui_pause_icon_get_556964(void);
void teleprompt_ui_title_pause_show_556a28(uint8_t show, uint8_t paused);
void teleprompt_ui_pause_hint_show_556ad4(void);
void teleprompt_ui_pause_hint_hide_556b00(void);
int32_t teleprompt_ui_action_pause_556b2c(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_resume_556b52(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_exit_556b78(uint8_t state, uint32_t reason);
int32_t teleprompt_ui_action_exit_animated_556bfe(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_gif_complete_556c44(uint8_t state, uint32_t arg);
int32_t teleprompt_ui_action_main_page_switch_prev_556cd8(uint8_t state, uint32_t packed);
int32_t teleprompt_ui_action_main_page_switch_next_556ed4(uint8_t state, uint32_t packed);
void teleprompt_ui_height_anim_exec_cb_557104(void *obj, int32_t height);
void teleprompt_ui_collapse_anim_ready_cb_55718c(void *anim);
void teleprompt_ui_collapse_animate_5571a8(uint8_t collapse);
int32_t teleprompt_ui_action_update_elapsed_time_557280(uint8_t state, uint32_t elapsed_sec);

#endif
