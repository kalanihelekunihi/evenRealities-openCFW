/* Private declarations for the EvenHub common list/text containers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_list_container.c (0x4dccd8..0x4dedc1)
 * and ...\EvenHub\common_text_container.c (from 0x4dee64; its scroll/event half starts at
 * 0x4df97c and is reconstructed separately). Shared by the two .c files in this
 * directory only; the EvenHub page (ui/a-14-evenhub-ui) reaches them through its own externs. */
#ifndef G2_COMMON_CONTAINERS_PRIVATE_H
#define G2_COMMON_CONTAINERS_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CC_SCREEN_W 576 /* clamp for x / width */
#define CC_SCREEN_H 288 /* clamp for y / height */
#define CC_MAX_BORDER_WIDTH 5u
#define CC_MAX_BORDER_COLOR 16u
#define CC_MAX_BORDER_RADIUS 10u
#define CC_MAX_PADDING 32u

#define LV_SIZE_CONTENT 0x3fffffff     /* LV_COORD_SET_SPEC(LV_COORD_MAX) */
#define LV_PART_SCROLLBAR 0x10000u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_OFF 0u
#define LV_SCROLLBAR_MODE_AUTO 3u
#define LV_LABEL_LONG_WRAP 0u
#define LV_LABEL_LONG_DOT 1u
#define LV_ANIM_OFF 0u

/* lv_anim_t as laid out by the stock LVGL 9.3 fork (96-byte stack frame). The stock code fills it
 * with the inline lv_anim_set_* helpers, i.e. plain stores. */
typedef struct cc_anim {
    void *var;                                  /* +0x00 */
    void (*exec_cb)(void *var, int32_t value);  /* +0x04 */
    void *custom_exec_cb;                       /* +0x08 */
    void *start_cb;                             /* +0x0c */
    void (*completed_cb)(struct cc_anim *);     /* +0x10 */
    void *deleted_cb;                           /* +0x14 */
    void *get_value_cb;                         /* +0x18 */
    void *user_data;                            /* +0x1c */
    int32_t (*path_cb)(void *);                 /* +0x20 */
    int32_t start_value;                        /* +0x24 */
    int32_t current_value;                      /* +0x28 */
    int32_t end_value;                          /* +0x2c */
    int32_t duration;                           /* +0x30 */
    int32_t act_time;                           /* +0x34 */
    uint32_t reverse_delay;                     /* +0x38 */
    uint32_t reverse_duration;                  /* +0x3c */
    uint8_t rest[0x20];                         /* +0x40 */
} cc_anim_t;
_Static_assert(sizeof(cc_anim_t) == 0x60, "stock anim frame is 96 bytes");
_Static_assert(offsetof(cc_anim_t, reverse_duration) == 0x3c, "anim reverse duration");

/* ---- common list container ---------------------------------------------------------------- */
#define COMMON_LIST_MAX_ITEMS 20u
#define COMMON_LIST_ITEM_HEIGHT 40
#define COMMON_LIST_NAME_LEN 64u

/* Events accepted by common_list_inject_event (EvenHub maps scroll up/down/click to 0/1/2). */
enum {
    COMMON_LIST_EVENT_DOWN = 0u,  /* focus moves to the next item */
    COMMON_LIST_EVENT_UP = 1u,    /* focus moves to the previous item */
    COMMON_LIST_EVENT_CLICK = 2u, /* report the focused item to the owner */
};

typedef int32_t (*common_list_event_cb_t)(int32_t index, const char *name, void *user);

/* Creation config (0x52c bytes, copied to the stack by common_list_create). */
typedef struct {
    uint32_t x, y, width, height;                         /* +0x00 */
    uint32_t border_width;                                /* +0x10 0..5 */
    uint32_t border_color;                                /* +0x14 grey index 0..16 */
    uint32_t border_radius;                               /* +0x18 0..10 */
    uint32_t padding;                                     /* +0x1c 0..32 */
    uint32_t item_count;                                  /* +0x20 1..20 */
    int32_t item_width;                                   /* +0x24 0 = fit text */
    uint8_t border_en;                                    /* +0x28 focus border on selected item */
    char item_name[COMMON_LIST_MAX_ITEMS][COMMON_LIST_NAME_LEN]; /* +0x29 */
    uint8_t reserved[3];
} common_list_config_t;
_Static_assert(sizeof(common_list_config_t) == 0x52c, "list config");

typedef struct {
    void *scroll_container;                              /* +0x000 lv_obj, the visible window */
    void *content_container;                             /* +0x004 lv_obj holding the items */
    void *items[COMMON_LIST_MAX_ITEMS];                  /* +0x008 one lv_obj (+ label child) each */
    int32_t item_count;                                  /* +0x058 */
    int32_t current_index;                               /* +0x05c focused item */
    int32_t scroll_offset;                               /* +0x060 first visible item */
    int32_t visible_height;                              /* +0x064 height - 2 * padding */
    int32_t visible_count;                               /* +0x068 visible_height / 40, >= 1 */
    uint8_t no_scroll;                                   /* +0x06c every item fits, centered */
    uint8_t border_en;                                   /* +0x06d */
    char names[COMMON_LIST_MAX_ITEMS][COMMON_LIST_NAME_LEN]; /* +0x06e */
    uint8_t reserved_56e[2];
    void *fifo;                                          /* +0x570 events queued during animations */
    common_list_event_cb_t event_cb;                     /* +0x574 */
    void *user_data;                                     /* +0x578 */
    uint8_t anim_busy;                                   /* +0x57c */
    uint8_t reserved_57d[3];
} common_list_t;
_Static_assert(offsetof(common_list_t, names) == 0x6e, "list names");
_Static_assert(offsetof(common_list_t, fifo) == 0x570, "list fifo");
_Static_assert(sizeof(common_list_t) == 0x580, "list handle");

/* ---- common text container ---------------------------------------------------------------- */
#define COMMON_TEXT_LEN 0x800u

typedef struct {
    int16_t x, y, width, height;       /* +0x00 */
    uint8_t border_width;              /* +0x08 */
    uint8_t border_color;              /* +0x09 grey index */
    uint8_t border_radius;             /* +0x0a */
    uint8_t padding;                   /* +0x0b */
    uint32_t text_color;               /* +0x0c 0xRRGGBB */
    uint8_t text_align;                /* +0x10 lv_text_align_t */
    char content[COMMON_TEXT_LEN];     /* +0x11 */
    uint8_t reserved[3];
} common_text_config_t;
_Static_assert(sizeof(common_text_config_t) == 0x814, "text config");

typedef int32_t (*common_text_event_cb_t)(uint8_t is_top, void *user);

typedef struct {
    void *scroll_container;            /* +0x000 */
    void *content_container;           /* +0x004 */
    void *text_label;                  /* +0x008 */
    int32_t max_scroll_y;              /* +0x00c */
    uint8_t at_top;                    /* +0x010 */
    uint8_t at_bottom;                 /* +0x011 */
    uint8_t scrollable;                /* +0x012 */
    uint8_t anim_busy;                 /* +0x013 */
    void *anim_target;                 /* +0x014 object of the running scroll animation */
    void *fifo;                        /* +0x018 */
    int32_t visible_height;            /* +0x01c height - 2 * padding */
    char text[COMMON_TEXT_LEN];        /* +0x020 */
    common_text_event_cb_t event_cb;   /* +0x820 */
    void *user_data;                   /* +0x824 */
} common_text_t;
_Static_assert(offsetof(common_text_t, event_cb) == 0x820, "text handle");
_Static_assert(sizeof(common_text_t) == 0x828, "text handle");

/* ---- stock helpers ------------------------------------------------------------------------ */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Both sinks are tested separately and every argument is evaluated per sink, as in stock.
 * Each including file defines cc_tag / cc_file. */
#define CC_LOG(level, func, line, cflags, text, short_text, ...)                                 \
    do {                                                                                         \
        if ((audio_log_flags() & 2u) != 0u)                                                      \
            audio_log_extended((level), cc_tag, cc_file, (func), (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                    \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);      \
    } while (0)

extern void *file_heap_allocate(uint32_t size); /* 0x474cd2 */
extern void file_heap_free(void *buffer);       /* 0x474d16 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */

/* Byte FIFO from the UI common API (0x206-byte heap ring). */
extern void *ui_common_api_fn_00509c1c(void);                                    /* create */
extern void ui_common_api_fn_00509c96(void *fifo);                               /* destroy */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push, 0 ok */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                            /* 1 empty */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len);  /* pop, bytes */
extern void ui_common_api_fn_00509f52(void *fifo);                               /* reset */

/* LVGL (stock fork). */
extern void *audio_uart_page_43de82(void *parent);                       /* lv_obj_create */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);            /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);        /* lv_obj_is_valid */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);     /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t width);            /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);           /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                           /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                    /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);               /* lv_obj_get_height */
extern void lv_obj_center_4409fa(void *obj);                             /* lv_obj_align(obj, CENTER, 0, 0) */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_441164(void *obj, int32_t v, uint32_t sel);  /* style width */
extern void audio_uart_page_441180(void *obj, int32_t v, uint32_t sel);  /* style max_width */
extern void audio_uart_page_4411aa(void *obj, int32_t v, uint32_t sel);  /* style max_height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_uart_page_delete_event_filter_44d7b8(void *obj);       /* lv_obj_delete */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);   /* lv_obj_get_child */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);            /* scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);             /* scroll_dir */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                    /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *obj);               /* lv_obj_get_scroll_top */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);            /* lv_obj_get_scroll_bottom */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim);
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_path_450672(void *anim);              /* ease_out */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);              /* ease_in_out */
extern void *audio_uart_page_499416(void *parent);                       /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);      /* lv_label_set_text */
extern void audio_uart_page_499678(void *label, uint32_t mode);          /* lv_label_set_long_mode */

extern uint32_t audio_uart_ring_primary_head_cell; /* RAM 0x200746dc: active lv_font_t * */

#endif
