/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * (log tag "onboarding.ui"). Native 0x4A8560..0x4AAB5D with literal pools
 * 0x4A8E56..0x4A8E6B, 0x4A910E..0x4A9117, 0x4A914C..0x4A915B,
 * 0x4A9190..0x4A9197, 0x4A91BA..0x4A91F3, 0x4A9386..0x4A93AF,
 * 0x4A99C8..0x4A99CF, 0x4A9BF8..0x4A9C0B, 0x4A9D6C..0x4A9D6F,
 * 0x4A9DD6..0x4A9DDF, 0x4A9E40..0x4A9E47, 0x4A9ED0..0x4A9EDB,
 * 0x4A9F66..0x4A9F83, 0x4AA02E..0x4AA047, 0x4AA0BC..0x4AA0C7,
 * 0x4AA14C..0x4AA16B, 0x4AA1F6..0x4AA26F, 0x4AAA48..0x4AAA4B,
 * 0x4AAA9C..0x4AAAA7, 0x4AAB46..0x4AAB4B (pools after 0x4AAB5E belong to the
 * page create/layout code that follows). The weather/battery refresh
 * 0x4A93B0 is in ui_onboarding_main_weather.c (double-precision FPU).
 *
 * Onboarding main page of the onboarding app (application id 0x10):
 * process 0 welcome (rotating roller), 1 "setting up", 2 touch tutorial
 * (substeps 0..14), 3 feature tiles (news / stock pages), 4 done. Key
 * events are mirrored to the peer as 8-byte sync records
 * {0, key, process_id, substep, x lo, x hi, y lo, y hi} and come back through
 * the reflash handler, which advances the tutorial. LVGL 9.3 fork:
 * style setters 0x44120e/0x44121c/0x44122a/0x441238 pad top/bottom/left/
 * right, 0x44127e LV_STYLE_BG_COLOR, 0x441488 LV_STYLE_OPA (98); align ids
 * 3 TOP_RIGHT, 15 OUT_BOTTOM_RIGHT, 17 OUT_LEFT_MID, 20 OUT_RIGHT_MID. */
#include <stdint.h>
#include <stddef.h>

/* lv_anim_t (LVGL 9.3 fork) as laid out on the stock 0x60-byte frame. */
typedef struct {
    void *var;                          /* +0x00 */
    void (*exec_cb)(void *, int32_t);   /* +0x04 */
    void *custom_exec_cb;               /* +0x08 */
    void *start_cb;                     /* +0x0c */
    void (*completed_cb)(void *);       /* +0x10 */
    void *deleted_cb;                   /* +0x14 */
    void *get_value_cb;                 /* +0x18 */
    void *user_data;                    /* +0x1c */
    int32_t (*path_cb)(void *);         /* +0x20 */
    int32_t start_value;                /* +0x24 */
    int32_t current_value;              /* +0x28 */
    int32_t end_value;                  /* +0x2c */
    int32_t duration;                   /* +0x30 */
    uint8_t rest[0x2c];                 /* +0x34 */
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "stock anim frame is 96 bytes");

/* Onboarding process record (RAM 0x200f4800). The other units declare only
 * the first three bytes; this page also keeps the step start tick at +4. */
typedef struct {
    uint8_t process_id;  /* +0 0 welcome, 1 setting up, 2 touch tips, 3 tiles, 4 done */
    uint8_t substep;     /* +1 */
    uint8_t status;      /* +2 */
    uint8_t reserved;    /* +3 */
    uint32_t step_tick;  /* +4 osKernelGetTickCount at the last ProcessStart */
} g2_onboarding_process_t;
_Static_assert(sizeof(g2_onboarding_process_t) == 8u, "process record");

/* Key sync record decoded from the 7 payload bytes after the type byte. */
typedef struct {
    uint8_t key;         /* +0 input event id */
    uint8_t process_id;  /* +1 sender's process */
    uint8_t substep;     /* +2 sender's substep */
    uint8_t reserved;    /* +3 */
    uint32_t value;      /* +4 payload bytes 3..6, little endian */
} g2_onboarding_key_msg_t;
_Static_assert(sizeof(g2_onboarding_key_msg_t) == 8u, "key sync record");

/* Input event ids (app page events). */
#define ONB_KEY_LONG_PRESS   0x08u
#define ONB_KEY_SINGLE_TAP   0x0au
#define ONB_KEY_SWIPE        0x44u /* data +0x10 -> int32_t[2] */
#define ONB_KEY_SWIPE_ALT    0x45u /* data +0x10 -> int32_t[2] */
#define ONB_KEY_DOUBLE_TAP   0x48u
#define ONB_KEY_49           0x49u
#define ONB_KEY_4A           0x4au
#define ONB_KEY_4B           0x4bu

#define ONB_APP_ID           0x10u
#define ONB_LV_OBJ_FLAG_HIDDEN 1u
#define ONB_ALIGN_TOP_RIGHT  3u
#define ONB_TILE_PITCH       304   /* 0x130, vertical distance between tiles */
#define ONB_PAGE_NARROW      352   /* 0x160 */
#define ONB_PAGE_WIDE        576   /* 0x240 */
#define ONB_ANIM_MS          250

/* RAM state (stock .bss/.data). */
extern g2_onboarding_process_t g2_onboarding_process; /* RAM 0x200f4800 */
extern void *g2_onboarding_mutex;                      /* RAM 0x20074830, osMutexId_t */
extern void *g2_onboarding_root_obj;                   /* RAM 0x20074834 */
extern void *g2_onboarding_event_fifo;                 /* RAM 0x20074cdc, ui_common byte FIFO */
extern void *g2_onboarding_main_obj_20074ce0;          /* RAM 0x20074ce0 scrolling tile list */
extern int32_t g2_onboarding_feature_page_open;        /* RAM 0x20074ce4 news/stock page expanded */
extern void *g2_onboarding_main_obj_20074ce8;          /* RAM 0x20074ce8 feature page container */
extern void *g2_onboarding_main_obj_20074cec;          /* RAM 0x20074cec welcome container */
extern void *g2_onboarding_main_obj_20074cf4;          /* RAM 0x20074cf4 welcome lv_roller */
extern void *g2_onboarding_main_obj_20074cf8;          /* RAM 0x20074cf8 status label */
extern void *g2_onboarding_main_obj_20074cfc;          /* RAM 0x20074cfc tip container */
extern void *g2_onboarding_main_obj_20074d08;          /* RAM 0x20074d08 tip label */
extern void *g2_onboarding_main_obj_20074d0c;          /* RAM 0x20074d0c indicator column */
extern void *g2_onboarding_main_obj_20074d10;          /* RAM 0x20074d10 hour label */
extern void *g2_onboarding_main_obj_20074d14;          /* RAM 0x20074d14 minute label */
extern void *g2_onboarding_main_obj_20074d30[6];       /* RAM 0x20074d30 tile objects, column 0 */
extern void *g2_onboarding_main_obj_20074d48[6];       /* RAM 0x20074d48 tile objects, column 1 */
extern void *g2_onboarding_main_obj_20074d60;          /* RAM 0x20074d60 side menu container */
extern void *g2_onboarding_main_obj_20074d64;          /* RAM 0x20074d64 */
extern void *g2_onboarding_main_obj_20074d68;          /* RAM 0x20074d68 */
extern int32_t g2_onboarding_tile_index;               /* RAM 0x20074d6c selected tile */
extern int32_t g2_onboarding_opened_page;              /* RAM 0x20074d70 0 news, 1 stock */
extern int32_t g2_onboarding_list_saved_y;             /* RAM 0x20074d78 */
extern int32_t g2_onboarding_anim_busy;                /* RAM 0x20074d7c */
extern int32_t g2_onboarding_main_flag_20074d88;       /* RAM 0x20074d88 */
extern int32_t g2_onboarding_stock_flag_20074db8;      /* RAM 0x20074db8 */
extern void *g2_onboarding_stock_obj_20074db4;         /* RAM 0x20074db4 */
extern uint8_t g2_onboarding_stock_page_20071048[];    /* RAM 0x20071048, +0x30 object */
extern uint8_t g2_onboarding_wait_peer_ack;            /* RAM 0x2007503d */
extern void *g2_onboarding_indicator_objs[];           /* RAM 0x20073c68 */
extern void *g2_onboarding_tile_list[6][2];            /* RAM 0x200734ec onboarding_tile_list */
extern int32_t g2_onboarding_indicator_count;          /* RAM 0x200042b4 (.data) */
extern int32_t g2_onboarding_scroll_duration;          /* RAM 0x20004284 (.data) */
extern int32_t g2_onboarding_bounce_distance;          /* RAM 0x20004288 (.data) */
extern int32_t g2_onboarding_bounce_duration;          /* RAM 0x2000428c (.data) */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* libc-like, RTOS, i18n. */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern uint32_t osKernelGetTickCount(void);                     /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                /* 0x45a568, 1 master */
extern uint32_t audio_uart_page_460084(const char *key);        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags); /* 0x464bb2 app data sync */
extern void audio_uart_master_display_stop(uint32_t app, const void *payload, uint16_t length,
                                           uint32_t extra);       /* 0x464c36 */
extern int32_t APP_PbNotifyEncodeOnboardingConfig(uint32_t type, const uint8_t *config); /* 0x4a7d4e */

/* LVGL. */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);       /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);       /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flags);
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y); /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);            /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);            /* lv_obj_set_y */
extern void audio_uart_page_43f506(void *obj, int32_t width);        /* lv_obj_set_width */
extern void audio_uart_page_43f66c(void *obj);                       /* lv_obj_update_layout */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                       /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_x_43fc70(void *obj);                /* lv_obj_get_x */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);            /* lv_obj_get_width */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t value, uint32_t selector); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t value, uint32_t selector); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t value, uint32_t selector); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t value, uint32_t selector); /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t selector); /* bg_color */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t selector); /* opa */
extern uint32_t audio_uart_lv_style_property_44bdea(void *obj, uint32_t selector,
                                                     uint32_t property); /* lv_obj_get_style_prop */
extern void *audio_uart_lv_obj_parent_44dca2(void *obj);             /* lv_obj_get_parent */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                /* lv_obj_get_scroll_y */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim);
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_path_45065a(void *anim);           /* lv_anim_path_ease_in */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);           /* lv_anim_path_ease_out */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);           /* lv_anim_path_ease_in_out */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void lv_roller_set_selected_50ebe2(void *roller, uint32_t index, uint32_t anim);
extern uint16_t lv_roller_get_selected_50ec94(void *roller);
extern uint16_t lv_roller_get_option_count_50ecee(void *roller);

/* ui_common byte FIFO and helpers. */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);       /* 1 empty, 0 has data */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* pop */
extern void ui_common_api_fn_00509f52(void *fifo);          /* reset */
extern int32_t ui_common_api_fn_00509f7a(int32_t *x, int32_t *y); /* page offset, both 0 */

/* Upstream LVGL header inlines emitted in this TU (upstream units, not hand-written):
 * 0x4A8560 lv_obj_get_style_opa, 0x4A856C lv_obj_set_style_pad_all. */
extern uint8_t ui_onboarding_main_sub_004A8560(void *obj, uint32_t part);

/* Sibling onboarding modules. */
extern void ui_onboarding_main_layout_4ab004(uint8_t step);
extern int32_t onboarding_news_page_refresh_50a094(void);
extern int32_t onboarding_news_key_handler_50a4ee(uint32_t key, void *data);
extern void onboarding_news_page_close_50a9c2(void);
extern int32_t onboarding_news_ext_event_handler_50aafc(const uint8_t *data, uint32_t len);
extern void onboarding_news_page_create_50ac5c(void *parent);
extern int32_t ui_onboarding_stock_sub_0050D578(const uint8_t *data, uint32_t len);
extern void ui_onboarding_stock_sub_0050D894(void *parent);
extern void ui_onboarding_stock_sub_0050DAB8(void);
extern int32_t ui_onboarding_stock_sub_0050DB34(const uint8_t *data, uint32_t len);
extern int32_t onboarding_animation_show_for_substep_50fc86(uint8_t substep);
extern void onboarding_animation_stop_all_50fe0e(void);
extern void onboarding_animation_tick_50fe56(void);
extern void ui_onboarding_main_sub_004A93B0(const uint8_t *data, uint32_t len); /* weather.c */

/* Functions in this file. */
void ui_onboarding_main_sub_004A859E(int32_t index, uint8_t alt_shade);
void ui_onboarding_main_sub_004A8610(void *anim);
void ui_onboarding_main_sub_004A865E(void *obj, int32_t y);
void ui_onboarding_main_sub_004A8668(void *obj, int32_t y);
void ui_onboarding_main_sub_004A8670(void *anim);
void ui_onboarding_main_sub_004A86C6(void *obj, int32_t opa);
void ui_onboarding_main_sub_004A86D2(void *anim);
void ui_onboarding_main_sub_004A8720(void *obj, int32_t opa);
void ui_onboarding_main_sub_004A872C(void *anim);
void ui_onboarding_main_sub_004A874C(void *anim);
void ui_onboarding_main_sub_004A87D0(void *obj, int32_t x);
void ui_onboarding_main_sub_004A87D8(void *anim);
void ui_onboarding_main_sub_004A8826(void *anim);
void ui_onboarding_main_sub_004A88AA(void);
void ui_onboarding_main_sub_004A8968(void);
void ui_onboarding_main_sub_004A8A24(void *anim);
void ui_onboarding_main_sub_004A8A82(int32_t direction);
void ui_onboarding_main_sub_004A8B30(void *obj, int32_t target, int32_t duration);
void ui_onboarding_main_sub_004A8B90(int32_t direction);
void ui_onboarding_main_sub_004A8C20(uint32_t key, void *data);
void ui_onboarding_main_sub_004A8D96(uint32_t key, void *data);
uint32_t ui_onboarding_main_sub_004A8DB6(uint32_t key);
uint32_t ui_onboarding_main_sub_004A8E6C(uint32_t key, void *data);
void ui_onboarding_main_sub_004A908C(void *obj, int32_t width);
void ui_onboarding_main_sub_004A90CC(void *obj, int32_t width);
void ui_onboarding_main_sub_004A9118(void *anim);
void ui_onboarding_main_sub_004A915C(void *anim);
void ui_onboarding_main_sub_004A9198(int32_t page);
int32_t ui_onboarding_main_sub_004A91F4(const uint8_t *data, uint32_t len);
void ui_onboarding_main_sub_004A95E8(void *obj);
void ui_onboarding_main_sub_004A9648(void *obj, uint8_t target, uint8_t mode);
void ui_onboarding_main_sub_004A96DC(uint8_t mode);
int32_t ui_onboarding_main_sub_004A979C(const uint8_t *raw, int32_t offset,
                                        g2_onboarding_key_msg_t *out);
uint32_t ui_onboarding_main_sub_004A97EA(const g2_onboarding_key_msg_t *msg);
uint32_t ui_onboarding_main_sub_004A99D0(const uint8_t *data, uint32_t len);
int32_t ui_onboarding_main_sub_004A9C0C(void);
void ui_onboarding_main_sub_004A9D70(void);
void ui_onboarding_main_sub_004A9DE0(void *parent);
void ui_onboarding_main_sub_004A9DE8(void);
void ui_onboarding_main_sub_004A9E48(void);
void ui_onboarding_main_sub_004A9EDC(void);
void ui_onboarding_main_sub_004A9F84(void);
void ui_onboarding_main_sub_004AA048(void);
void ui_onboarding_main_sub_004AA0C8(void);
void ui_onboarding_main_sub_004AA16C(void);
void ui_onboarding_main_sub_004AA270(uint8_t substep);
void ui_onboarding_main_sub_004AAA4C(void);
void ui_onboarding_main_sub_004AAAA8(void);
void ui_onboarding_main_sub_004AAB4C(void);

/* Stock strings. */
static const char module_tag[] = "onboarding.ui"; /* ROM 0x789de0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\ui_onboarding_main_page.c"; /* ROM 0x6eaab0 */
static const char menu_show_fn[] = "onboarding_menu_show_with_animation"; /* ROM 0x75c570 */
static const char menu_hide_fn[] = "onboarding_menu_hide_with_animation"; /* ROM 0x75c5b8 */
static const char menu_null[] = "onboarding_menu_container is NULL"; /* ROM 0x75c594 */
static const char menu_null_short[] = "[onboarding.ui]onboarding_menu_container is NULL"; /* ROM 0x72ff60 */
static const char tileview_fn[] = "onboarding_tileview_ext_event_handler"; /* ROM 0x750914 */
static const char bad_args[] = "len = %d, raw_data = %p"; /* ROM 0x77d3fc */
static const char bad_args_short[] = "[onboarding.ui]len = %d, raw_data = %p"; /* ROM 0x75093c */
static const char timeout_exit[] = "onboarding timeout exit event"; /* ROM 0x767710 */
static const char timeout_exit_short[] = "[onboarding.ui]onboarding timeout exit event"; /* ROM 0x73a8d4 */
static const char reflash_fn[] = "Onboarding_ReflashEventHandler"; /* ROM 0x767730 */
static const char time_update[] = "update time display,hour = %d,min = %d"; /* ROM 0x750964 */
static const char time_update_short[] =
    "[onboarding.ui]update time display,hour = %d,min = %d"; /* ROM 0x725610 */
static const char two_digits[] = "%1d %1d"; /* ROM 0x78ed4c */
static const char process_start_fn[] = "Onboarding_ProcessStart"; /* ROM 0x77d414 */
static const char process_next_fn[] = "Onboarding_ProcessNext"; /* ROM 0x77d444 */
static const char unknown_process[] = "Unknown process_id: %d"; /* ROM 0x77d42c */
static const char unknown_process_short[] = "[onboarding.ui]Unknown process_id: %d"; /* ROM 0x75098c */
static const char touch_tips_fn[] = "Onboarding_ShowTouchTips"; /* ROM 0x774154 */
static const char unknown_substep[] = "Unknown touch substep: %d"; /* ROM 0x774170 */
static const char unknown_substep_short[] = "[onboarding.ui]Unknown touch substep: %d"; /* ROM 0x745fe4 */
static const char id_setting_up[] = "ID_ONBOARDING_SETTING_UP"; /* ROM 0x774138 */
static const char id_reconnect[] = "ID_ONBOARDING_RECONNECT_REMINDER"; /* ROM 0x75c5dc */
static const char id_activate[] = "ID_ONBOARDING_DOUBLE_TAP_TO_ACTIVATE"; /* ROM 0x7509b4 */
static const char id_switch[] = "ID_ONBOARDING_SWIPE_TO_SWITCH"; /* ROM 0x767750 */
static const char id_expand[] = "ID_ONBOARDING_SINGLE_TAP_TO_EXPAND"; /* ROM 0x75c600 */
static const char id_return[] = "ID_ONBOARDING_DOUBLE_TAP_TO_RETURN"; /* ROM 0x75c624 */
static const char id_access[] = "ID_ONBOARDING_LONG_PRESS_TO_ACCESS"; /* ROM 0x75c648 */
static const char id_close[] = "ID_ONBOARDING_DOUBLE_TAP_TO_CLOSE"; /* ROM 0x75c66c */
static const char id_again[] = "ID_ONBOARDING_DOUBLE_TAP_AGAIN"; /* ROM 0x767770 */

/* Both sinks are tested separately and every argument is evaluated per sink, as in stock. */
#define ONB_LOG(level, func, line, cflags, text, short_text, ...)                              \
    do {                                                                                       \
        if ((audio_log_flags() & 2u) != 0u)                                                    \
            audio_log_extended((level), module_tag, source_file, (func), (line), (text),       \
                               ##__VA_ARGS__);                                                 \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                  \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);    \
    } while (0)

#define ONB_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))
#define ONB_OPA(obj, opa) audio_uart_display_audio_reset_441488((obj), (opa), 0u)

/* Inlined in every animation-completed callback: replay one key record that
 * was queued while the animation was running. */
#define ONB_REPLAY_QUEUED_KEY()                                                                \
    do {                                                                                       \
        if (g2_onboarding_event_fifo != NULL &&                                                \
            ui_common_api_fn_00509dfa(g2_onboarding_event_fifo) == 0) {                        \
            uint8_t raw_[12];                                                                  \
            g2_onboarding_key_msg_t msg_;                                                      \
            audio_uart_buffer_zero(raw_, 10u, 0u);                                             \
            (void)ui_common_api_fn_00509e14(g2_onboarding_event_fifo, raw_, 7u);               \
            if (ui_onboarding_main_sub_004A979C(raw_, 0, &msg_) == 0)                          \
                (void)ui_onboarding_main_sub_004A97EA(&msg_);                                  \
        }                                                                                      \
    } while (0)

#define ONB_RESET_QUEUED_KEYS(fifo)                                                            \
    do {                                                                                       \
        if ((fifo) != NULL && ui_common_api_fn_00509dfa(fifo) == 0)                            \
            ui_common_api_fn_00509f52(fifo);                                                   \
    } while (0)

/* Page indicator dots: the selected one white, the rest 0x222222 (0x444444
 * while the list is dimmed). */
void ui_onboarding_main_sub_004A859E(int32_t index, uint8_t alt_shade)
{
    for (int32_t i = 0; i < g2_onboarding_indicator_count; i++) {
        if (g2_onboarding_indicator_objs[i] == NULL)
            continue;
        if (i == index)
            audio_uart_page_44127e(g2_onboarding_indicator_objs[i],
                                   audio_uart_page_44104c(0xffffffu), 0u);
        else if (alt_shade == 0u)
            audio_uart_page_44127e(g2_onboarding_indicator_objs[i],
                                   audio_uart_page_44104c(0x222222u), 0u);
        else
            audio_uart_page_44127e(g2_onboarding_indicator_objs[i],
                                   audio_uart_page_44104c(0x444444u), 0u);
    }
}

/* Tile scroll finished. */
void ui_onboarding_main_sub_004A8610(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    ONB_REPLAY_QUEUED_KEY();
}

void ui_onboarding_main_sub_004A865E(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void ui_onboarding_main_sub_004A8668(void *obj, int32_t y)
{
    audio_uart_page_43f142(obj, y);
}

/* Edge bounce finished. */
void ui_onboarding_main_sub_004A8670(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    g2_onboarding_main_flag_20074d88 = 0;
    ONB_REPLAY_QUEUED_KEY();
}

void ui_onboarding_main_sub_004A86C6(void *obj, int32_t opa)
{
    ONB_OPA(obj, (uint8_t)opa);
}

/* Fade-in finished. */
void ui_onboarding_main_sub_004A86D2(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    ONB_REPLAY_QUEUED_KEY();
}

void ui_onboarding_main_sub_004A8720(void *obj, int32_t opa)
{
    ONB_OPA(obj, (uint8_t)opa);
}

/* Timeout fade-out finished: the master asks the app manager to stop app 0x10. */
void ui_onboarding_main_sub_004A872C(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    if (audio_uart_device_role_get() == 1u)
        audio_uart_master_display_stop(ONB_APP_ID, NULL, 0u, 0u);
}

/* Tutorial fade-out finished: after substep 14 move to process 3 and report
 * onboarding config {3, 0} to the phone. */
void ui_onboarding_main_sub_004A874C(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    if (g2_onboarding_process.process_id == 2u && g2_onboarding_process.substep >= 14u) {
        uint8_t config[2] = {3u, 0u}; /* ROM 0x78f6c6 */
        g2_onboarding_process.process_id = 3u;
        g2_onboarding_process.substep = 0u;
        g2_onboarding_wait_peer_ack = 0u;
        (void)APP_PbNotifyEncodeOnboardingConfig(0u, config);
        ui_onboarding_main_sub_004A9EDC();
    }
    ONB_REPLAY_QUEUED_KEY();
}

void ui_onboarding_main_sub_004A87D0(void *obj, int32_t x)
{
    audio_uart_page_43f0e0(obj, x);
}

/* Menu slide-in finished. */
void ui_onboarding_main_sub_004A87D8(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    ONB_REPLAY_QUEUED_KEY();
}

/* Menu slide-out finished: restore the list. */
void ui_onboarding_main_sub_004A8826(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    ONB_OPA(g2_onboarding_main_obj_20074d0c, 0xffu);
    ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
    ONB_OPA(g2_onboarding_main_obj_20074ce0, 0xffu);
    ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
    ONB_REPLAY_QUEUED_KEY();
}

/* onboarding_menu_show_with_animation */
void ui_onboarding_main_sub_004A88AA(void)
{
    g2_lv_anim_t a;
    if (g2_onboarding_main_obj_20074d60 == NULL) {
        ONB_LOG(2u, menu_show_fn, 0x1ecu, 0x08000000u, menu_null, menu_null_short);
        return;
    }
    audio_uart_page_43f66c(g2_onboarding_main_obj_20074d60);
    int32_t start = -audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d60, start);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_onboarding_main_obj_20074d60;
    audio_uart_lv_anim_values_4506ce(&a, start, 0);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A87D0;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = ui_onboarding_main_sub_004A87D8;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* onboarding_menu_hide_with_animation */
void ui_onboarding_main_sub_004A8968(void)
{
    g2_lv_anim_t a;
    if (g2_onboarding_main_obj_20074d60 == NULL) {
        ONB_LOG(2u, menu_hide_fn, 0x218u, 0x08000000u, menu_null, menu_null_short);
        return;
    }
    int32_t x = audio_uart_lv_obj_x_43fc70(g2_onboarding_main_obj_20074d60);
    audio_uart_page_43f66c(g2_onboarding_main_obj_20074d60);
    int32_t end = -audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_onboarding_main_obj_20074d60;
    audio_uart_lv_anim_values_4506ce(&a, x, end);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A87D0;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = ui_onboarding_main_sub_004A8826;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Bounce out finished: animate the list back to its saved y. */
void ui_onboarding_main_sub_004A8A24(void *anim)
{
    g2_lv_anim_t a;
    (void)anim;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_onboarding_main_obj_20074ce0;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_43fce0(g2_onboarding_main_obj_20074ce0),
                                     g2_onboarding_list_saved_y);
    a.duration = g2_onboarding_bounce_duration;
    a.exec_cb = ui_onboarding_main_sub_004A8668;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = ui_onboarding_main_sub_004A8670;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Rubber-band bounce when scrolling past the first or last tile. */
void ui_onboarding_main_sub_004A8A82(int32_t direction)
{
    g2_lv_anim_t a;
    int32_t target;
    if (g2_onboarding_main_obj_20074ce0 == NULL)
        return;
    g2_onboarding_list_saved_y = audio_uart_lv_obj_y_43fce0(g2_onboarding_main_obj_20074ce0);
    if (direction == 1 && g2_onboarding_tile_index >= g2_onboarding_indicator_count - 1)
        target = g2_onboarding_list_saved_y - g2_onboarding_bounce_distance;
    else if (direction == -1 && g2_onboarding_tile_index < 1)
        target = g2_onboarding_bounce_distance + g2_onboarding_list_saved_y;
    else
        return;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_onboarding_main_obj_20074ce0;
    audio_uart_lv_anim_values_4506ce(&a, g2_onboarding_list_saved_y, target);
    a.duration = g2_onboarding_bounce_duration;
    a.exec_cb = ui_onboarding_main_sub_004A8668;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = ui_onboarding_main_sub_004A8A24;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Scroll the tile list from its current scroll y to target. */
void ui_onboarding_main_sub_004A8B30(void *obj, int32_t target, int32_t duration)
{
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(obj), target);
    a.duration = duration;
    a.exec_cb = ui_onboarding_main_sub_004A865E;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = ui_onboarding_main_sub_004A8610;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Move the tile selection by one (+1 down, -1 up), bouncing at the ends. */
void ui_onboarding_main_sub_004A8B90(int32_t direction)
{
    if (g2_onboarding_main_obj_20074ce0 == NULL || g2_onboarding_anim_busy != 0)
        return;
    int32_t y = audio_uart_lv_obj_y_44e498(g2_onboarding_main_obj_20074ce0);
    if (direction == 1 && g2_onboarding_tile_index < g2_onboarding_indicator_count - 1) {
        g2_onboarding_tile_index++;
        ui_onboarding_main_sub_004A8B30(g2_onboarding_main_obj_20074ce0, ONB_TILE_PITCH + y,
                                        g2_onboarding_scroll_duration);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        return;
    }
    if (direction == -1 && g2_onboarding_tile_index >= 1) {
        g2_onboarding_tile_index--;
        ui_onboarding_main_sub_004A8B30(g2_onboarding_main_obj_20074ce0, y - ONB_TILE_PITCH,
                                        g2_onboarding_scroll_duration);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        return;
    }
    ui_onboarding_main_sub_004A8A82(direction);
}

/* Key sync from the opened stock page (record type 0 on app 0x10). The swipe
 * record (0x44) is built with 8 bytes but only 6 are sent, as in stock. */
void ui_onboarding_main_sub_004A8C20(uint32_t key, void *data)
{
    if (key == ONB_KEY_SINGLE_TAP) {
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_SINGLE_TAP;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = 0u;
        pkt[5] = 0u;
        pkt[6] = 0u;
        pkt[7] = 0u;
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_DOUBLE_TAP) {
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_DOUBLE_TAP;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = 0u;
        pkt[5] = 0u;
        pkt[6] = 0u;
        pkt[7] = 0u;
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_4B) {
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_4B;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = 0u;
        pkt[5] = 0u;
        pkt[6] = 0u;
        pkt[7] = 0u;
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_49) {
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_49;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = 0u;
        pkt[5] = 0u;
        pkt[6] = 0u;
        pkt[7] = 0u;
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_SWIPE_ALT) {
        const int32_t *point = *(const int32_t *const *)(const void *)((const uint8_t *)data + 0x10u);
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_SWIPE_ALT;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = (uint8_t)point[0];
        pkt[5] = (uint8_t)(point[0] >> 8);
        pkt[6] = (uint8_t)point[1];
        pkt[7] = (uint8_t)(point[1] >> 8);
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_SWIPE) {
        const int32_t *point = *(const int32_t *const *)(const void *)((const uint8_t *)data + 0x10u);
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_SWIPE;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = (uint8_t)point[0];
        pkt[5] = (uint8_t)(point[0] >> 8);
        pkt[6] = (uint8_t)point[1];
        pkt[7] = (uint8_t)(point[1] >> 8);
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 6u, 0u);
    }
}

/* Keys while a feature page is open go to that page. */
void ui_onboarding_main_sub_004A8D96(uint32_t key, void *data)
{
    if (g2_onboarding_opened_page == 0)
        (void)onboarding_news_key_handler_50a4ee(key, data);
    else if (g2_onboarding_opened_page == 1)
        ui_onboarding_main_sub_004A8C20(key, data);
}

/* Which key the current tutorial step (process 2) or tile view (process 3)
 * accepts. */
uint32_t ui_onboarding_main_sub_004A8DB6(uint32_t key)
{
    uint8_t substep = g2_onboarding_process.substep;
    switch (g2_onboarding_process.process_id) {
    case 2u:
        switch (substep) {
        case 0u:
            return key == ONB_KEY_DOUBLE_TAP ? 1u : 0u;
        case 2u:
            return key == ONB_KEY_SWIPE ? 1u : 0u;
        case 4u:
            return key == ONB_KEY_SINGLE_TAP ? 1u : 0u;
        case 6u:
            return key == ONB_KEY_DOUBLE_TAP ? 1u : 0u;
        case 8u:
            return key == ONB_KEY_LONG_PRESS ? 1u : 0u;
        case 11u:
            return key == ONB_KEY_DOUBLE_TAP ? 1u : 0u;
        case 13u:
            return key == ONB_KEY_DOUBLE_TAP ? 1u : 0u;
        default:
            return 0u;
        }
    case 3u:
        if (key == ONB_KEY_4B)
            return g2_onboarding_wait_peer_ack == 1u ? 0u : 1u;
        if (key == ONB_KEY_49)
            return 1u;
        return 0u;
    default:
        return 0u;
    }
}

/* Page key handler: accepted keys are mirrored as type-0 sync records unless
 * an animation runs; with a feature page open they go to that page. */
uint32_t ui_onboarding_main_sub_004A8E6C(uint32_t key, void *data)
{
    if (ui_onboarding_main_sub_004A8DB6(key) == 0u)
        return 0u;
    if (g2_onboarding_feature_page_open != 0) {
        if (g2_onboarding_anim_busy != 0)
            return 0u;
        ui_onboarding_main_sub_004A8D96(key, data);
        return 0u;
    }
    if (g2_onboarding_anim_busy != 0)
        return 0u;
    if (key == ONB_KEY_SWIPE) {
        const int32_t *point = *(const int32_t *const *)(const void *)((const uint8_t *)data + 0x10u);
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_SWIPE;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = (uint8_t)point[0];
        pkt[5] = (uint8_t)(point[0] >> 8);
        pkt[6] = (uint8_t)point[1];
        pkt[7] = (uint8_t)(point[1] >> 8);
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_SWIPE_ALT) {
        const int32_t *point = *(const int32_t *const *)(const void *)((const uint8_t *)data + 0x10u);
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = ONB_KEY_SWIPE_ALT;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = (uint8_t)point[0];
        pkt[5] = (uint8_t)(point[0] >> 8);
        pkt[6] = (uint8_t)point[1];
        pkt[7] = (uint8_t)(point[1] >> 8);
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    } else if (key == ONB_KEY_4A || key == ONB_KEY_SINGLE_TAP || key == ONB_KEY_DOUBLE_TAP ||
               key == ONB_KEY_4B || key == ONB_KEY_49 || key == ONB_KEY_LONG_PRESS) {
        uint8_t pkt[8];
        pkt[0] = 0u;
        pkt[1] = (uint8_t)key;
        pkt[2] = g2_onboarding_process.process_id;
        pkt[3] = g2_onboarding_process.substep;
        pkt[4] = 0u;
        pkt[5] = 0u;
        pkt[6] = 0u;
        pkt[7] = 0u;
        (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 8u, 0u);
    }
    return 0u;
}

/* Feature page expand step: widen the container and push the indicator
 * column left by the same amount. */
void ui_onboarding_main_sub_004A908C(void *obj, int32_t width)
{
    int32_t x;
    int32_t y;
    audio_uart_page_43f506(obj, width);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d0c, -(width - ONB_PAGE_NARROW), y);
    audio_uart_page_43f6d6(obj, audio_uart_lv_obj_parent_44dca2(obj), ONB_ALIGN_TOP_RIGHT, 0, 0);
}

/* Feature page collapse step. */
void ui_onboarding_main_sub_004A90CC(void *obj, int32_t width)
{
    int32_t x;
    int32_t y;
    audio_uart_page_43f506(obj, width);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d0c, (x - width) + ONB_PAGE_NARROW, y);
    audio_uart_page_43f6d6(obj, audio_uart_lv_obj_parent_44dca2(obj), ONB_ALIGN_TOP_RIGHT, 0, 0);
}

/* Expand finished: build the opened page and drop queued keys. */
void ui_onboarding_main_sub_004A9118(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    g2_onboarding_feature_page_open = 1;
    ui_onboarding_main_sub_004A9198(g2_onboarding_opened_page);
    ONB_RESET_QUEUED_KEYS(g2_onboarding_event_fifo);
}

/* Collapse finished. */
void ui_onboarding_main_sub_004A915C(void *anim)
{
    (void)anim;
    g2_onboarding_anim_busy = 0;
    g2_onboarding_feature_page_open = 0;
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    ONB_RESET_QUEUED_KEYS(g2_onboarding_event_fifo);
}

void ui_onboarding_main_sub_004A9198(int32_t page)
{
    if (page == 0)
        onboarding_news_page_create_50ac5c(g2_onboarding_main_obj_20074ce8);
    else if (page == 1)
        ui_onboarding_main_sub_004A9DE0(g2_onboarding_main_obj_20074ce8);
}

/* onboarding_tileview_ext_event_handler: records received while a feature
 * page is open. Stock passes callee results through in r0 where they exist. */
int32_t ui_onboarding_main_sub_004A91F4(const uint8_t *data, uint32_t len)
{
    if (len == 0u || data == NULL) {
        ONB_LOG(1u, tileview_fn, 0x537u, 0x04800000u, bad_args, bad_args_short, len, data);
        return 0;
    }
    switch (data[0]) {
    case 0u:
        if (g2_onboarding_opened_page == 0)
            return onboarding_news_ext_event_handler_50aafc(data, len);
        if (g2_onboarding_opened_page == 1)
            return ui_onboarding_stock_sub_0050D578(data, len);
        return 0;
    case 1u:
        ui_onboarding_main_sub_004A93B0(data + 1, len - 1u);
        return 0;
    case 3u:
        if (g2_onboarding_opened_page != 0)
            return onboarding_news_page_refresh_50a094();
        return 0;
    case 4u:
        return ui_onboarding_stock_sub_0050DB34(data + 1, len - 1u);
    case 8u:
        ONB_LOG(3u, tileview_fn, 0x56du, 0x0c000000u, timeout_exit, timeout_exit_short);
        ui_onboarding_main_sub_004A96DC(1u);
        return 0;
    case 10u:
        if (len >= 2u && data[1] == 1u)
            ui_onboarding_main_sub_004AA16C();
        else
            ui_onboarding_main_sub_004A9EDC();
        return 0;
    case 11u:
        if (len >= 2u && g2_onboarding_main_obj_20074cf4 != NULL) {
            uint8_t index = data[1];
            if (index < lv_roller_get_option_count_50ecee(g2_onboarding_main_obj_20074cf4))
                lv_roller_set_selected_50ebe2(g2_onboarding_main_obj_20074cf4, index, 1u);
        }
        return 0;
    case 12u:
        if (data[1] >= g2_onboarding_process.substep) {
            g2_onboarding_process.substep = data[1];
            ui_onboarding_main_sub_004A9F84();
        }
        return 0;
    case 17u:
        ui_onboarding_main_sub_004A96DC(0u);
        return 0;
    default:
        return 0;
    }
}

/* Fade obj in from its current opacity to 255. */
void ui_onboarding_main_sub_004A95E8(void *obj)
{
    g2_lv_anim_t a;
    g2_onboarding_anim_busy = 1;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, ui_onboarding_main_sub_004A8560(obj, 0u), 0xff);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A86C6;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = ui_onboarding_main_sub_004A86D2;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Fade obj to target; mode 1 ends in the timeout exit callback. */
void ui_onboarding_main_sub_004A9648(void *obj, uint8_t target, uint8_t mode)
{
    g2_lv_anim_t a;
    g2_onboarding_anim_busy = 1;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, ui_onboarding_main_sub_004A8560(obj, 0u), target);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A8720;
    a.path_cb = audio_uart_lv_anim_path_450672;
    if (mode == 1u)
        a.completed_cb = ui_onboarding_main_sub_004A872C;
    else
        a.completed_cb = ui_onboarding_main_sub_004A874C;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Fade the whole page (or only the open feature page) out; mode 1 is the
 * timeout exit. */
void ui_onboarding_main_sub_004A96DC(uint8_t mode)
{
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    if (g2_onboarding_feature_page_open == 1) {
        audio_uart_page_43ded4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
        if (g2_onboarding_stock_flag_20074db8 == 1 &&
            audio_uart_lv_obj_has_flag_43e0e0(g2_onboarding_stock_obj_20074db4,
                                              ONB_LV_OBJ_FLAG_HIDDEN) == 0u)
            audio_uart_page_43ded4(*(void **)(void *)(g2_onboarding_stock_page_20071048 + 0x30u),
                                   ONB_LV_OBJ_FLAG_HIDDEN);
        a.var = g2_onboarding_main_obj_20074ce8;
    } else {
        a.var = g2_onboarding_root_obj;
    }
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A8720;
    a.path_cb = audio_uart_lv_anim_path_450672;
    if (mode == 1u)
        a.completed_cb = ui_onboarding_main_sub_004A872C;
    else
        a.completed_cb = ui_onboarding_main_sub_004A874C;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Decode a key sync record at raw + offset. */
int32_t ui_onboarding_main_sub_004A979C(const uint8_t *raw, int32_t offset,
                                        g2_onboarding_key_msg_t *out)
{
    if (raw == NULL || out == NULL)
        return -1;
    out->key = raw[offset];
    out->process_id = raw[offset + 1];
    out->substep = raw[offset + 2];
    out->value = (uint32_t)raw[offset + 3] | ((uint32_t)raw[offset + 4] << 8) |
                 ((uint32_t)raw[offset + 5] << 16) | ((uint32_t)raw[offset + 6] << 24);
    return 0;
}

/* Apply a key sync record: advance the tutorial substep when the expected
 * gesture arrives, expand the selected tile on single tap, start the
 * process-3 tile view on 0x4b. Returns 1 only when the expand is refused
 * because an animation runs. */
uint32_t ui_onboarding_main_sub_004A97EA(const g2_onboarding_key_msg_t *msg)
{
    uint8_t key = msg->key;
    uint8_t substep = msg->substep;
    g2_lv_anim_t a;

    if (msg->process_id == 2u) {
        switch (substep) {
        case 0u:
            if (key == ONB_KEY_DOUBLE_TAP) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 1u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
            }
            break;
        case 2u:
            if (key == ONB_KEY_SWIPE) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 3u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
                ui_onboarding_main_sub_004A8B90(1);
            }
            break;
        case 4u:
            if (key == ONB_KEY_SINGLE_TAP) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 5u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
                if (g2_onboarding_feature_page_open == 0) {
                    if (g2_onboarding_anim_busy != 0)
                        return 1u;
                    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
                    audio_uart_lv_anim_init_4503d6(&a);
                    a.var = g2_onboarding_main_obj_20074ce8;
                    audio_uart_lv_anim_values_4506ce(&a, ONB_PAGE_NARROW, ONB_PAGE_WIDE);
                    a.duration = ONB_ANIM_MS;
                    a.exec_cb = ui_onboarding_main_sub_004A908C;
                    a.path_cb = audio_uart_lv_anim_path_450672;
                    a.completed_cb = ui_onboarding_main_sub_004A9118;
                    g2_onboarding_anim_busy = 1;
                    g2_onboarding_opened_page = g2_onboarding_tile_index;
                    (void)audio_uart_lv_anim_start_450408(&a);
                }
            }
            break;
        case 6u:
            break;
        case 8u:
            if (key == ONB_KEY_LONG_PRESS) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 9u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
            }
            break;
        case 11u:
            if (key == ONB_KEY_DOUBLE_TAP) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 12u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
            }
            break;
        case 13u:
            if (key == ONB_KEY_DOUBLE_TAP) {
                (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
                g2_onboarding_process.substep = 14u;
                (void)osMutexRelease(g2_onboarding_mutex);
                ui_onboarding_main_sub_004A9EDC();
            }
            break;
        default:
            break;
        }
    } else if (msg->process_id == 3u) {
        if (key == ONB_KEY_4B) {
            g2_onboarding_wait_peer_ack = 1u;
            g2_onboarding_process.step_tick = osKernelGetTickCount();
            ui_onboarding_main_sub_004AAB4C();
        }
    }
    return 0u;
}

/* Onboarding_ReflashEventHandler: app data records for the main page
 * (type byte first). With a feature page open everything goes to the
 * tileview handler. */
uint32_t ui_onboarding_main_sub_004A99D0(const uint8_t *data, uint32_t len)
{
    if (g2_onboarding_feature_page_open == 1) {
        (void)ui_onboarding_main_sub_004A91F4(data, len);
        return 0u;
    }
    switch (data[0]) {
    case 0u:
        if (g2_onboarding_anim_busy != 0) {
            (void)ui_common_api_fn_00509ca2(g2_onboarding_event_fifo, data + 1, 7u);
            return 0u;
        } else {
            g2_onboarding_key_msg_t msg;
            if (ui_onboarding_main_sub_004A979C(data, 1, &msg) == 0)
                (void)ui_onboarding_main_sub_004A97EA(&msg);
        }
        break;
    case 1u:
        ui_onboarding_main_sub_004A93B0(data + 1, len - 1u);
        break;
    case 3u:
        (void)onboarding_news_page_refresh_50a094();
        break;
    case 4u:
        (void)ui_onboarding_stock_sub_0050DB34(data + 1, len - 1u);
        break;
    case 7u: {
        char hour_text[12];
        char minute_text[12];
        uint8_t hour;
        uint8_t minute;
        ONB_LOG(3u, reflash_fn, 0x764u, 0x0c800000u, time_update, time_update_short,
                (uint32_t)data[1], (uint32_t)data[2]);
        audio_uart_buffer_zero(hour_text, 10u, 0u);
        audio_uart_buffer_zero(hour_text, 10u, 0u);
        hour = data[1];
        minute = data[2];
        (void)audio_ble_format_to_buffer(hour_text, two_digits, (int32_t)hour / 10,
                                         (int32_t)hour % 10);
        (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074d10, hour_text);
        audio_uart_buffer_zero(minute_text, 10u, 0u);
        audio_uart_buffer_zero(minute_text, 10u, 0u);
        (void)audio_ble_format_to_buffer(minute_text, two_digits, (int32_t)minute / 10,
                                         (int32_t)minute % 10);
        (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074d14, minute_text);
        break;
    }
    case 8u:
        ONB_LOG(3u, reflash_fn, 0x772u, 0x0c000000u, timeout_exit, timeout_exit_short);
        ui_onboarding_main_sub_004A96DC(1u);
        break;
    case 10u:
        if (len >= 2u && data[1] == 1u)
            ui_onboarding_main_sub_004AA16C();
        else
            ui_onboarding_main_sub_004A9EDC();
        break;
    case 11u:
        if (len >= 2u && g2_onboarding_main_obj_20074cf4 != NULL) {
            uint8_t index = data[1];
            if (index < lv_roller_get_option_count_50ecee(g2_onboarding_main_obj_20074cf4))
                lv_roller_set_selected_50ebe2(g2_onboarding_main_obj_20074cf4, index, 1u);
        }
        break;
    case 12u:
        if (data[1] >= g2_onboarding_process.substep) {
            g2_onboarding_process.substep = data[1];
            ui_onboarding_main_sub_004A9F84();
        }
        break;
    case 17u:
        ui_onboarding_main_sub_004A96DC(0u);
        break;
    default:
        break;
    }
    return 0u;
}

/* Page tick (UI registry event 4). The master drives the peer: welcome
 * roller every 6 s ({0x0b, index}), auto-advance of the non-interactive
 * tutorial substeps after 1.5 s / 2.5 s ({0x0c, substep}) and the process-3
 * close after 3 s ({0x11}). */
int32_t ui_onboarding_main_sub_004A9C0C(void)
{
    onboarding_animation_tick_50fe56();
    if (g2_onboarding_process.step_tick == 0u) {
        g2_onboarding_process.step_tick = osKernelGetTickCount();
        return 0;
    }
    uint8_t role = audio_uart_device_role_get();
    uint32_t elapsed = osKernelGetTickCount() - g2_onboarding_process.step_tick;
    switch (g2_onboarding_process.process_id) {
    case 0u:
        if (g2_onboarding_main_obj_20074cf4 != NULL) {
            uint16_t count = lv_roller_get_option_count_50ecee(g2_onboarding_main_obj_20074cf4);
            if (count != 0u) {
                uint32_t index = (elapsed / 6000u) % count;
                if ((uint16_t)index != lv_roller_get_selected_50ec94(g2_onboarding_main_obj_20074cf4) &&
                    role == 1u) {
                    uint8_t pkt[2] = {0x0bu, 0x00u}; /* ROM 0x78f6c8 */
                    pkt[1] = (uint8_t)index;
                    (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 2u, 0u);
                }
            }
        }
        break;
    case 2u: {
        uint8_t substep = g2_onboarding_process.substep;
        if (substep == 1u || substep == 3u || substep == 5u || substep == 7u || substep == 9u ||
            substep == 12u) {
            if (elapsed >= 1500u && role == 1u) {
                uint8_t pkt[2] = {0x0cu, 0x00u}; /* ROM 0x78f6ca */
                pkt[1] = substep;
                (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 2u, 0u);
            }
        } else if (substep == 10u) {
            if (elapsed >= 2500u && role == 1u) {
                uint8_t pkt[2] = {0x0cu, 0x00u}; /* ROM 0x78f6cc */
                pkt[1] = 10u;
                (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 2u, 0u);
            }
        }
        break;
    }
    case 3u:
        if (g2_onboarding_wait_peer_ack == 1u && elapsed >= 3000u) {
            g2_onboarding_wait_peer_ack = 0u;
            if (role == 1u) {
                uint8_t pkt[1] = {0x11u}; /* ROM 0x78f6f4 */
                (void)audio_uart_master_display_refresh(ONB_APP_ID, pkt, 1u, 0u);
            }
        }
        break;
    default:
        break;
    }
    return 0;
}

/* Fill onboarding_tile_list[6][2] from the tile object globals. */
void ui_onboarding_main_sub_004A9D70(void)
{
    g2_onboarding_tile_list[0][0] = g2_onboarding_main_obj_20074d30[0];
    g2_onboarding_tile_list[0][1] = g2_onboarding_main_obj_20074d48[0];
    g2_onboarding_tile_list[1][0] = g2_onboarding_main_obj_20074d30[1];
    g2_onboarding_tile_list[1][1] = g2_onboarding_main_obj_20074d48[1];
    g2_onboarding_tile_list[2][0] = g2_onboarding_main_obj_20074d30[2];
    g2_onboarding_tile_list[2][1] = g2_onboarding_main_obj_20074d48[2];
    g2_onboarding_tile_list[3][0] = g2_onboarding_main_obj_20074d30[3];
    g2_onboarding_tile_list[3][1] = g2_onboarding_main_obj_20074d48[3];
    g2_onboarding_tile_list[4][0] = g2_onboarding_main_obj_20074d30[4];
    g2_onboarding_tile_list[4][1] = g2_onboarding_main_obj_20074d48[4];
    g2_onboarding_tile_list[5][0] = g2_onboarding_main_obj_20074d30[5];
    g2_onboarding_tile_list[5][1] = g2_onboarding_main_obj_20074d48[5];
}

void ui_onboarding_main_sub_004A9DE0(void *parent)
{
    ui_onboarding_stock_sub_0050D894(parent);
}

/* Collapse the open feature page (576 -> 352). */
void ui_onboarding_main_sub_004A9DE8(void)
{
    g2_lv_anim_t a;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = g2_onboarding_main_obj_20074ce8;
    audio_uart_lv_anim_values_4506ce(&a, ONB_PAGE_WIDE, ONB_PAGE_NARROW);
    a.duration = ONB_ANIM_MS;
    a.exec_cb = ui_onboarding_main_sub_004A90CC;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = ui_onboarding_main_sub_004A915C;
    g2_onboarding_anim_busy = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Close the open feature page immediately (no animation). */
void ui_onboarding_main_sub_004A9E48(void)
{
    int32_t x;
    int32_t y;
    if (g2_onboarding_main_obj_20074ce8 == NULL)
        return;
    if (g2_onboarding_opened_page == 0)
        onboarding_news_page_close_50a9c2();
    else if (g2_onboarding_opened_page == 1)
        ui_onboarding_stock_sub_0050DAB8();
    audio_uart_page_43f506(g2_onboarding_main_obj_20074ce8, ONB_PAGE_NARROW);
    audio_uart_page_43f6d6(g2_onboarding_main_obj_20074ce8,
                           audio_uart_lv_obj_parent_44dca2(g2_onboarding_main_obj_20074ce8),
                           ONB_ALIGN_TOP_RIGHT, 0, 0);
    (void)ui_common_api_fn_00509f7a(&x, &y);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d0c, x, y);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    g2_onboarding_feature_page_open = 0;
    g2_onboarding_anim_busy = 0;
    ONB_RESET_QUEUED_KEYS(g2_onboarding_event_fifo);
}

/* Onboarding_ProcessStart: show the screen for the current process. */
void ui_onboarding_main_sub_004A9EDC(void)
{
    g2_onboarding_process.step_tick = osKernelGetTickCount();
    switch (g2_onboarding_process.process_id) {
    case 0u:
        ui_onboarding_main_sub_004AA048();
        break;
    case 1u:
        ui_onboarding_main_sub_004AA0C8();
        break;
    case 2u:
        ui_onboarding_main_sub_004AA270(g2_onboarding_process.substep);
        break;
    case 3u:
        ui_onboarding_main_sub_004AAA4C();
        break;
    case 4u:
        break;
    default:
        ONB_LOG(2u, process_start_fn, 0x87au, 0x08400000u, unknown_process, unknown_process_short,
                (uint32_t)g2_onboarding_process.process_id);
        break;
    }
}

/* Onboarding_ProcessNext: 0 -> 1 -> 2 (substeps) ... 3 -> 4. */
void ui_onboarding_main_sub_004A9F84(void)
{
    (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
    switch (g2_onboarding_process.process_id) {
    case 0u:
        g2_onboarding_process.process_id = 1u;
        g2_onboarding_process.substep = 0u;
        break;
    case 1u:
        g2_onboarding_process.process_id = 2u;
        g2_onboarding_process.substep = 0u;
        break;
    case 2u:
        g2_onboarding_process.substep++;
        break;
    case 3u:
        g2_onboarding_process.process_id = 4u;
        g2_onboarding_process.substep = 0u;
        break;
    case 4u:
        break;
    default:
        ONB_LOG(2u, process_next_fn, 0x8a6u, 0x08400000u, unknown_process, unknown_process_short,
                (uint32_t)g2_onboarding_process.process_id);
        (void)osMutexRelease(g2_onboarding_mutex);
        return;
    }
    (void)osMutexRelease(g2_onboarding_mutex);
    ui_onboarding_main_sub_004A9EDC();
}

/* Process 0: welcome screen with the roller reset to its first option. */
void ui_onboarding_main_sub_004AA048(void)
{
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cf4, ONB_LV_OBJ_FLAG_HIDDEN);
    lv_roller_set_selected_50ebe2(g2_onboarding_main_obj_20074cf4, 0u, 0u);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cf8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);
}

/* Process 1: "setting up" status text. */
void ui_onboarding_main_sub_004AA0C8(void)
{
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cf4, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cf8, ONB_LV_OBJ_FLAG_HIDDEN);
    (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074cf8, ONB_TR(id_setting_up));
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);
}

/* Record 10 with argument 1: reconnect reminder text. */
void ui_onboarding_main_sub_004AA16C(void)
{
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cf4, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cf8, ONB_LV_OBJ_FLAG_HIDDEN);
    (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074cf8, ONB_TR(id_reconnect));
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);
}

/* Shared tail of the tutorial steps that keep the side menu parked off-screen. */
#define ONB_MENU_PARK_LEFT()                                                                   \
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d60,                                    \
                           -audio_uart_lv_obj_width_43fd9e(g2_onboarding_main_obj_20074d60), 0)

/* Even substeps show a tip (animation, layout, localized text); odd ones
 * show the result before the tick auto-advances. */
#define ONB_SHOW_TIP(substep, key)                                                             \
    do {                                                                                       \
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0xffu);                                       \
        (void)onboarding_animation_show_for_substep_50fc86(substep);                           \
        ui_onboarding_main_layout_4ab004(substep);                                             \
        (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074d08, ONB_TR(key));            \
    } while (0)

/* Onboarding_ShowTouchTips: tutorial screen for each process-2 substep. */
void ui_onboarding_main_sub_004AA270(uint8_t substep)
{
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);

    switch (substep) {
    case 0u:
        if (g2_onboarding_feature_page_open == 1)
            ui_onboarding_main_sub_004A9E48();
        if (g2_onboarding_main_obj_20074ce0 != NULL) {
            audio_uart_lv_scroll_to_y_44ea04(g2_onboarding_main_obj_20074ce0, 0, 0u);
            g2_onboarding_tile_index = 0;
            ui_onboarding_main_sub_004A859E(0, 0u);
        }
        ONB_SHOW_TIP(substep, id_activate);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 1u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0u);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        ui_onboarding_main_sub_004A95E8(g2_onboarding_main_obj_20074d0c);
        ui_onboarding_main_sub_004A95E8(g2_onboarding_main_obj_20074ce0);
        break;
    case 2u:
        ONB_SHOW_TIP(substep, id_switch);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 3u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0xffu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0xffu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 4u:
        ONB_SHOW_TIP(substep, id_expand);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 5u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0u);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0xffu);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 6u:
        ONB_SHOW_TIP(substep, id_return);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0x7fu);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 7u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0xffu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0xffu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0xffu);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 8u:
        ONB_SHOW_TIP(substep, id_access);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0xffu);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 9u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0xffu);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        ui_onboarding_main_sub_004A88AA();
        break;
    case 10u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        audio_uart_page_43f09a(g2_onboarding_main_obj_20074d60, 0, 0);
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0xffu);
        break;
    case 11u:
        ONB_SHOW_TIP(substep, id_close);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        audio_uart_page_43f09a(g2_onboarding_main_obj_20074d60, 0, 0);
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 12u:
        ONB_OPA(g2_onboarding_main_obj_20074cfc, 0u);
        onboarding_animation_stop_all_50fe0e();
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        ui_onboarding_main_sub_004A8968();
        break;
    case 13u:
        ONB_SHOW_TIP(substep, id_again);
        ONB_OPA(g2_onboarding_main_obj_20074d0c, 0x7fu);
        ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 1u);
        ONB_OPA(g2_onboarding_main_obj_20074ce0, 0x7fu);
        ONB_OPA(g2_onboarding_main_obj_20074ce8, 0u);
        ONB_MENU_PARK_LEFT();
        ONB_OPA(g2_onboarding_main_obj_20074d64, 0u);
        ONB_OPA(g2_onboarding_main_obj_20074d68, 0u);
        break;
    case 14u:
        ui_onboarding_main_sub_004A9648(g2_onboarding_main_obj_20074cfc, 0u, 0u);
        ui_onboarding_main_sub_004A9648(g2_onboarding_main_obj_20074d0c, 0u, 0u);
        ui_onboarding_main_sub_004A9648(g2_onboarding_main_obj_20074ce0, 0u, 0u);
        break;
    default:
        ONB_LOG(2u, touch_tips_fn, 0xa36u, 0x08400000u, unknown_substep, unknown_substep_short,
                (uint32_t)substep);
        break;
    }
}

/* Process 3 entry: hide everything until the peer confirms (key 0x4b). */
void ui_onboarding_main_sub_004AAA4C(void)
{
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    onboarding_animation_stop_all_50fe0e();
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);
}

/* Process 3 tile view: first tile, indicator and list fully visible. */
void ui_onboarding_main_sub_004AAAA8(void)
{
    if (g2_onboarding_feature_page_open == 1)
        ui_onboarding_main_sub_004A9E48();
    if (g2_onboarding_main_obj_20074ce0 != NULL) {
        audio_uart_lv_scroll_to_y_44ea04(g2_onboarding_main_obj_20074ce0, 0, 0u);
        g2_onboarding_tile_index = 0;
        ui_onboarding_main_sub_004A859E(0, 0u);
    }
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cec, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cfc, ONB_LV_OBJ_FLAG_HIDDEN);
    onboarding_animation_stop_all_50fe0e();
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d0c, ONB_LV_OBJ_FLAG_HIDDEN);
    ONB_OPA(g2_onboarding_main_obj_20074d0c, 0xffu);
    ui_onboarding_main_sub_004A859E(g2_onboarding_tile_index, 0u);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074ce0, ONB_LV_OBJ_FLAG_HIDDEN);
    ONB_OPA(g2_onboarding_main_obj_20074ce0, 0xffu);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d60, ONB_LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d68, ONB_LV_OBJ_FLAG_HIDDEN);
}

void ui_onboarding_main_sub_004AAB4C(void)
{
    ui_onboarding_main_sub_004AAAA8();
    ui_onboarding_main_sub_004A95E8(g2_onboarding_root_obj);
}
