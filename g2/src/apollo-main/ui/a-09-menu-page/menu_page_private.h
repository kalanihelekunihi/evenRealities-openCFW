/* Private declarations for the main menu page, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c (log tag "menu.page").
 * Shared by menu_page_navigation.c and menu_page_ui.c in this directory only. */
#ifndef G2_MENU_PAGE_PRIVATE_H
#define G2_MENU_PAGE_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* One menu row; same layout as the kvMenuConfigureValue mirror. */
typedef struct {
    const void *icon;      /* +0x00 lv_image_dsc_t *, NULL draws a 20x20 placeholder */
    char text[32];         /* +0x04 i18n key (or literal name when app_type != 0) */
    uint32_t text_res;     /* +0x24 action id 1..8, 0xffe = external (Evenhub) app */
    uint8_t app_type;      /* +0x28 non-zero: text is a literal, not an i18n key */
    uint8_t reserved[3];
    int32_t icon_num;      /* +0x2c */
    int32_t app_id;        /* +0x30 */
} g2_menu_page_item_t;
_Static_assert(sizeof(g2_menu_page_item_t) == 0x34, "menu page item");

#define G2_MENU_ITEM_MAX 20
#define G2_MENU_DEFAULT_ITEM_COUNT 8
#define G2_MENU_VISIBLE_ROWS 5

/* LVGL 9 lv_anim_t as laid out in the stock build (0x60 bytes). */
typedef struct {
    void *var;                 /* +0x00 */
    void *exec_cb;             /* +0x04 */
    void *custom_exec_cb;      /* +0x08 */
    void *start_cb;            /* +0x0c */
    void *completed_cb;        /* +0x10 */
    void *deleted_cb;          /* +0x14 */
    void *get_value_cb;        /* +0x18 */
    void *user_data;           /* +0x1c */
    void *path_cb;             /* +0x20 */
    int32_t start_value;       /* +0x24 */
    int32_t current_value;     /* +0x28 */
    int32_t end_value;         /* +0x2c */
    int32_t duration;          /* +0x30 */
    int32_t act_time;          /* +0x34 */
    uint32_t playback_delay;   /* +0x38 */
    uint32_t playback_duration;/* +0x3c */
    uint8_t rest[0x20];        /* +0x40 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "lv_anim_t");

/* Two-word usage record handed to the persistence/telemetry gateway (key 0x40101). */
typedef struct {
    uint32_t app;    /* +0x0 */
    uint32_t source; /* +0x4 always 1 from the menu */
} g2_menu_launch_record_t;

/* Menu page RAM state (names shared with ../a-08-menu-page/menu_page.c). */
extern g2_menu_page_item_t g2_menu_display_items[G2_MENU_ITEM_MAX]; /* RAM 0x2006a8fc active rows */
extern g2_menu_page_item_t g2_menu_page_items[G2_MENU_ITEM_MAX];    /* RAM 0x2006ad0c configured rows */
extern const g2_menu_page_item_t g2_menu_builtin_apps[G2_MENU_DEFAULT_ITEM_COUNT]; /* ROM 0x6c2198 */
extern void *g2_menu_item_objs[G2_MENU_ITEM_MAX];       /* RAM 0x20072c18 row objects */
extern void *g2_menu_focus_anim_obj;    /* RAM 0x200746ec menu root object, NULL until init */
extern void *g2_menu_frame_obj;         /* RAM 0x200746f0 bordered list frame */
extern void *g2_menu_list_obj;          /* RAM 0x200746f4 scrolling viewport */
extern void *g2_menu_content_container; /* RAM 0x200746f8 row container */
extern int32_t g2_menu_use_ext_items;   /* RAM 0x200746fc */
extern int32_t g2_menu_ext_item_count;  /* RAM 0x20074700 */
extern int32_t g2_menu_item_count;      /* RAM 0x20074704 */
extern int32_t g2_menu_current_index;   /* RAM 0x20074708 */
extern int32_t g2_menu_scroll_offset;   /* RAM 0x2007470c first visible row */
extern volatile uint8_t g2_menu_anim_in_progress; /* RAM 0x20074fe4 */
extern const int32_t g2_menu_item_height;         /* ROM 0x78f2c8 = 50 */
extern uint32_t audio_uart_ring_secondary_head_cell; /* RAM 0x200746e0: menu lv_font_t * */
extern uint32_t audio_uart_display_audio_handle;     /* RAM 0x200744d0 page stack */
extern uint8_t audio_uart_registry_context_20002ca8[]; /* RAM 0x20002ca8 page context, +4 = root */

/* Logging (stock helpers). */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Both sinks are tested separately and every argument is evaluated per sink, as in stock. */
#define MENU_LOG(level, func, line, cflags, text, short_text, ...)                            \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), menu_module_tag, menu_source_file, (func), (line),    \
                               (text), ##__VA_ARGS__);                                        \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* libc-like and i18n helpers. */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);         /* memset(p, n, c) 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);    /* memcpy 0x439be4 */
extern uint32_t g2_log_module_length(const char *);                     /* strlen 0x44a43c */
extern int32_t audio_uart_font_path_compare(const char *, const char *); /* strcmp 0x46cacc */
extern uint32_t audio_uart_page_460084(const char *);                   /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *, uint32_t);      /* localized text */

#define MENU_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))
#define MENU_ITEM_TR(i) MENU_TR(g2_menu_display_items[(i)].text)

/* Menu page module siblings. */
extern void menu_page_mutex_init_460178(void);
extern void menu_page_mutex_lock_46018e(void);
extern void menu_page_mutex_unlock_4601ea(void);
extern int32_t menu_event_fifo_push_460242(const uint8_t *data, uint16_t len);
extern void menu_event_fifo_reset_460344(void);
extern void resume_menu_anim_time_460374(void);
extern int32_t menu_calculate_scroll_position_for_item_460d6c(int32_t index);
extern void menu_scroll_anim_start_460fc6(void *obj, int32_t target, int32_t duration);
extern void menu_focus_change_anim_start_4612f8(void);
extern void menu_trigger_rubber_band_effect_46137c(bool at_top);
extern void style_pad_all_460128(void *obj, int32_t value, uint32_t selector);
extern void menu_obj_set_style_transform_scale_46015a(void *obj, int32_t value, uint32_t selector);

/* Functions in this directory. */
void menu_inject_event_461620(uint8_t event);
void menu_inject_event_absolute_462594(int32_t index);
int32_t menu_find_item_by_name_4628c4(const char *item_name);
void menu_jump_to_item_instant_462a7c(int32_t index);
void menu_item_styles_hook_462db4(void);
void menu_update_item_styles_462db6(void);
void *menu_item_icon_create_462ea8(void *parent, int32_t index);
int32_t menu_key_event_send_462f38(uint32_t key, const void *context);
uint32_t menu_key_handler_463204(uint32_t unused0, uint32_t unused1, uint32_t key,
                                 const void *context);
int32_t menu_reflash_event_handler_46302c(const uint8_t *data, uint32_t len);
uint32_t audio_uart_registry_callback_46327e(uint32_t event, const uint8_t *data, uint32_t len,
                                             void *parent);

#endif
