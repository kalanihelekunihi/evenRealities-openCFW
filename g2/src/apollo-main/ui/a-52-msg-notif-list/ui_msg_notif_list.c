/* Message notification list UI, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\ui_msg_notif_list.c
 * (log tag "message_notify_list.ui"). Native 0x54fa56..0x551e99 (functions
 * 0x54fa56..0x54ff59, 0x54ff64..0x5505cb, 0x5505d0..0x550687, 0x550694..0x5506eb,
 * 0x550708..0x550809, 0x550820..0x550947, 0x550968..0x550afd, 0x550b14..0x550bed,
 * 0x550bf4..0x550cb7, 0x550cc4..0x550d2f, 0x550d3c..0x550eb5, 0x550ed0..0x550f7b,
 * 0x550f8c..0x550fef, 0x551018..0x551306, 0x55131c..0x5514d3, 0x5514f0..0x551805,
 * 0x551814..0x551a9f, 0x551abc..0x551e53, 0x551e5c..0x551e99) with interleaved
 * literal pools. 0x54fa24 is the IAR out-of-line copy of LVGL's inline
 * lv_obj_set_style_pad_all (upstream lv_obj_style.h, not reconstructed here).
 * The rest of the TU (message_notify_ui_reflash 0x551ed8, page init/deinit
 * 0x55225c / 0x552820) is reconstructed separately.
 *
 * The list is a vertical LVGL tileview (UI context RAM 0x2006f734 +0x3c) with
 * one 548x214 tile per ANCC notification, newest first; a column of up to ten
 * 8 px indicator dots (+0x10..) sits in a 3-dot scrolling window (+0x0c).
 * A ten-row binding table (RAM 0x20071db8) maps tile index <-> message index
 * <-> ANCC record. Inputs are forwarded to the master arm as 6-byte page
 * records {3, code, value, 0, 0, 0} on app 4; while an animation runs
 * (state byte RAM 0x2007503c: 1 scroll, 2 bounce, 3 add, 4 delete) the page
 * queues records in the ui_common_api FIFO and the scroll-complete callback
 * replays one per animation. Relative timestamps come from the ANCS date
 * string "YYYYMMDDTHHMMSS". */
#include <stdint.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

#define MSG_NOTIF_MAX_BINDINGS 10
#define MSG_NOTIF_MAX_DOTS 10
#define MSG_NOTIF_TILE_HEIGHT 214      /* 0xd6 */
#define MSG_NOTIF_DOT_STEP 12          /* 8 px dot + 4 px gap */
#define MSG_NOTIF_VISIBLE_DOTS 3
#define LV_SIZE_CONTENT_FORK 0x3fffffff
#define LV_OBJ_FLAG_HIDDEN 1u
#define LV_OBJ_FLAG_CLICKABLE_SCROLLABLE 0x12u
#define LV_DIR_VER 0x0cu
#define COLOR_WHITE 0xffffffu
#define COLOR_DIM 0x444444u

enum {
    MSG_NOTIF_ANIM_IDLE = 0u,
    MSG_NOTIF_ANIM_SCROLL = 1u,
    MSG_NOTIF_ANIM_BOUNCE = 2u,
    MSG_NOTIF_ANIM_ADD = 3u,
    MSG_NOTIF_ANIM_DELETE = 4u,
};

enum {
    INPUT_CLICK = 0x0au,
    INPUT_SCROLL_UP = 0x44u,
    INPUT_SCROLL_DOWN = 0x45u,
    INPUT_JUMP = 0x46u,
    INPUT_CLOSE = 0x48u,
};

enum { PAGE_RECORD_INPUT = 3u, PAGE_RECORD_BASICINFO = 4u };
enum { DEVICE_ROLE_MASTER = 1u };
enum { MSG_NOTIF_APP_ID = 4u };

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

/* am_hal_rtc_time_t word layout (40 bytes), as in system/a-03-service-time. */
typedef struct {
    uint32_t read_error; /* +0 */
    uint32_t weekday;    /* +4 index into the "Sun".."Sat" table */
    uint32_t century;    /* +8 */
    uint32_t year;       /* +12 years since 2000 */
    uint32_t month;      /* +16 */
    uint32_t day;        /* +20 */
    uint32_t hour;       /* +24 */
    uint32_t minute;     /* +28 */
    uint32_t second;     /* +32 */
    uint32_t hundredths; /* +36 */
} g2_rtc_time_t;
_Static_assert(sizeof(g2_rtc_time_t) == 40u, "am_hal_rtc_time_t");

/* ANCC record, as in app/a-15-ancc-service/service_ancc.c. */
typedef struct {
    uint32_t uid;              /* +0x000 */
    uint8_t category_id;       /* +0x004 ANCS CategoryID (0..11) */
    uint8_t event_id;          /* +0x005 ANCS EventID (0..2) */
    uint8_t event_flags;       /* +0x006 ANCS EventFlags (5 bits) */
    uint8_t reserved_007;
    char app_identifier[64];   /* +0x008 */
    char display_name[32];     /* +0x048 */
    char title[64];            /* +0x068 */
    char subtitle[64];         /* +0x0a8 */
    char message[512];         /* +0x0e8 */
    char date[16];             /* +0x2e8 */
    uint8_t action;            /* +0x2f8 */
    uint8_t reserved_2f9[3];
} g2_ancc_notification_t;
_Static_assert(offsetof(g2_ancc_notification_t, date) == 0x2e8u, "date");
_Static_assert(sizeof(g2_ancc_notification_t) == 0x2fcu, "ANCS notification");

typedef struct g2_ancc_record {
    g2_ancc_notification_t notif;   /* +0x000 */
    uint8_t used;                   /* +0x2fc */
    uint8_t reserved_2fd[3];
    struct g2_ancc_record *next;    /* +0x300 */
} g2_ancc_record_t;
_Static_assert(sizeof(g2_ancc_record_t) == 0x304u, "ANCC record");

/* One row of the tile binding table (RAM 0x20071db8, 10 x 12 bytes). */
typedef struct {
    void *tile;                 /* +0x0 tileview tile */
    g2_ancc_record_t *msg;      /* +0x4 ANCC record shown on it */
    uint8_t msg_index;          /* +0x8 0 = newest */
    uint8_t tile_index;         /* +0x9 */
    uint8_t valid;              /* +0xa */
    uint8_t reserved;           /* +0xb */
} g2_msg_tile_binding_t;
_Static_assert(sizeof(g2_msg_tile_binding_t) == 12u, "binding row");

/* Card content objects (msg_notif_create_content_obj clears 0x1c bytes). */
typedef struct {
    void *obj;          /* +0x00 */
    void *app_name;     /* +0x04 label, top left */
    void *title;        /* +0x08 label */
    void *separator;    /* +0x0c 24x24 image between title and subtitle */
    void *subtitle;     /* +0x10 label */
    void *time;         /* +0x14 label, top right */
    void *detail;       /* +0x18 message body label, at most 90 px */
} g2_msg_notif_content_t;
_Static_assert(sizeof(g2_msg_notif_content_t) == 0x1cu, "content objects");

/* One tile (msg_notif_create_msg_item clears 0x28 bytes). */
typedef struct {
    void *tile;                       /* +0x00 */
    void *card;                       /* +0x04 bordered card */
    void *icon;                       /* +0x08 30x30 app icon */
    g2_msg_notif_content_t content;   /* +0x0c */
} g2_msg_notif_item_t;
_Static_assert(sizeof(g2_msg_notif_item_t) == 0x28u, "message item");

/* UI context (RAM 0x2006f734). The item count is not established here; the
 * code indexes items by a tile index below ten. */
typedef struct {
    uint8_t reserved_00[8];                       /* +0x00 */
    void *empty_label;                            /* +0x08 shown with no messages */
    void *indicator;                              /* +0x0c dot column viewport */
    void *dots[MSG_NOTIF_MAX_DOTS];               /* +0x10 */
    void *indicator_edge;                         /* +0x38 */
    void *tileview;                               /* +0x3c */
    g2_msg_notif_item_t items[MSG_NOTIF_MAX_BINDINGS]; /* +0x40 */
} g2_msg_notif_ui_t;
_Static_assert(offsetof(g2_msg_notif_ui_t, tileview) == 0x3cu, "tileview");
_Static_assert(offsetof(g2_msg_notif_ui_t, items) == 0x40u, "items");

extern g2_msg_tile_binding_t g2_msg_tile_bindings_20071db8[MSG_NOTIF_MAX_BINDINGS]; /* RAM 0x20071db8 */
extern g2_msg_notif_ui_t g2_msg_notif_ui_2006f734;              /* RAM 0x2006f734 */
extern uint8_t g2_msg_notif_anim_busy;                          /* RAM 0x2007503c */
extern int32_t g2_msg_notif_current_index_20074cd0;             /* RAM 0x20074cd0 */
extern int32_t g2_msg_notif_original_y_20074cd4;                /* RAM 0x20074cd4 bounce origin */
extern void *g2_msg_notif_event_fifo;                           /* RAM 0x20074cd8 g2_ui_fifo_t * */
extern void *g2_msg_notif_page;                                 /* RAM 0x20074710 */
extern int8_t g2_msg_notif_delete_tile_20004554;                /* RAM 0x20004554, -1 none */
extern int8_t g2_msg_notif_delete_count_20004555;               /* RAM 0x20004555 count before delete */
extern int8_t g2_msg_notif_delete_visible_20004556;             /* RAM 0x20004556 min(count, 3) */
extern int32_t g2_msg_notif_scroll_duration_20004278;           /* RAM .data 0x20004278 */
extern int32_t g2_msg_notif_bounce_distance_2000427c;           /* RAM .data 0x2000427c */
extern int32_t g2_msg_notif_bounce_duration_20004280;           /* RAM .data 0x20004280 */
extern const char *g2_msg_notif_weekday_keys_2000425c[7];       /* RAM .data 0x2000425c i18n keys */
extern uint32_t audio_system_alert_font_200746e0;               /* RAM 0x200746e0 active lv_font_t * */
extern const uint8_t g2_msg_notif_separator_icon_76e248[];      /* ROM 0x76e248 lv_image_dsc_t 24x24 */
extern const uint8_t g2_msg_notif_card_icon_769804[];           /* ROM 0x769804 lv_image_dsc_t 30x30 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t g2_log_module_length(const char *text);                          /* 0x44a43c strlen */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern int32_t atoi_48d868(const char *text);                                    /* 0x48d868 */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b);      /* 0x46cacc strcmp */
extern int32_t iar_abs_509694(int32_t value);                                    /* 0x509694 */
extern uint32_t service_time_calendar_to_epoch_wrapper(const g2_rtc_time_t *time); /* 0x44a192 */
extern void service_time_current_calendar_get(g2_rtc_time_t *time);             /* 0x44a19a */
extern uint32_t service_time_current_epoch_get(void);                           /* 0x44a1c6 */
extern uint32_t audio_time_format_mode_46650c(void);            /* 1 = 12-hour */
extern uint8_t svc_universal_setting_get_date_format_466500(void); /* 0/1 month first */
extern uint32_t rtc_weekday_from_date_4d3cf8(uint32_t year, uint32_t month, uint32_t day);
extern uint32_t audio_uart_page_460084(const char *key);                   /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern uint32_t audio_settings_unread_message_count(void);  /* service_ancc_message_count_get 0x4974d4 */
extern g2_ancc_record_t *service_ancc_record_find(uint8_t index);         /* 0x49758e */
extern void service_ancc_record_remove(g2_ancc_record_t *record);         /* 0x497826 */
/* TSV names; by behaviour 0x588598 sets an app icon image from an app
 * identifier and 0x588550 maps an app identifier to a display name. */
extern void navigation_apply_named_resource(void *image, const char *app_identifier); /* 0x588598 */
extern const char *navigation_record_third_field_lookup(const char *app_identifier);  /* 0x588550 */
extern uint8_t audio_uart_device_role_get(void);                          /* 0x45a568 */
extern void audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                              uint32_t flags);            /* 0x464bb2 */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t flags);

extern void *audio_uart_page_43de82(void *parent);                         /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);              /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);              /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag); /* lv_obj_has_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);       /* lv_obj_set_pos */
extern void audio_uart_page_43f142(void *obj, int32_t y);                  /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);       /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                  /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                  /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                             /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                             /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                      /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);                  /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                 /* lv_obj_get_height */
extern void audio_lv_delete_44d7b8(void *obj);                             /* lv_obj_delete */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);     /* lv_obj_get_child */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                      /* lv_obj_get_scroll_y */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern uint32_t audio_uart_page_44104c(uint32_t hex);                      /* lv_color_hex */
extern void audio_uart_page_4411aa(void *obj, int32_t v, uint32_t sel);    /* max_height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);    /* pad_top */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);    /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel); /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);    /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);    /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void lv_obj_set_style_pad_all_54fa24(void *obj, int32_t v, uint32_t sel); /* inline copy */
extern void *audio_uart_page_498668(void *parent);                         /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);          /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                         /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);         /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *label, uint32_t mode);     /* lv_label_set_long_mode */
extern const char *audio_uart_page_text_pointer_4997f8(const void *label); /* lv_label_get_text */
extern void *lv_tileview_add_tile_50ff0e(void *tileview, uint8_t col, uint8_t row, uint32_t dir);
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *a);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *a, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *a);
extern int32_t audio_uart_lv_anim_default_path_450634(void *anim);         /* lv_anim_path_linear */
extern int32_t audio_uart_lv_anim_path_45065a(void *anim);
extern int32_t audio_uart_lv_anim_path_450672(void *anim);
extern int32_t audio_uart_lv_anim_path_450688(void *anim);                 /* lv_anim_path_ease_in_out */

/* Rest of ui_msg_notif_list.c. */
extern void message_notify_ui_reflash_551ed8(void *page, uint8_t animate);

void msg_notif_virtual_scroll_tileview_550820(int32_t direction);
void msg_notif_jump_to_message_absolute_550968(uint32_t index);
void msg_notif_delete_virtual_scroll_tileview_550b14(int32_t direction);
void msg_indicator_update_550e2e(int32_t index, uint8_t animate);
void msg_indicator_scroll_to_550eda(int32_t index, uint32_t duration, int32_t direction);
void msg_indicator_scroll_anim_550ef4(int32_t count, int32_t index, uint32_t duration,
                                      int32_t direction);
void msg_indicator_fade_out_550f8c(uint8_t index);
void msg_indicator_fade_complete_cb_551018(void *anim);
int32_t msg_notif_last_index_5511bc(void);
void msg_notif_add_message_5511ce(void *page);
void msg_notif_remove_current_message_551240(void);
void msg_notif_remove_message_5512b0(g2_ancc_record_t *msg);
void msg_notif_hide_message_55131c(g2_ancc_record_t *msg);

static const char module[] = "message_notify_list.ui"; /* ROM 0x77d36c */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\ui_msg_notif_list.c"; /* ROM 0x6f0ad8 */

static const char fmt_s[] = "%s";                       /* ROM 0x54fe80 / 0x55016c (code literal) */
static const char am_text[] = "AM";                     /* ROM 0x54ff5c */
static const char pm_text[] = "PM";                     /* ROM 0x54ff60 */
static const char key_now[] = "ID_GENERAL_NOW";         /* ROM 0x789db0 */
static const char key_in_min_2[] = "ID_NOTIFICATION_IN_MIN_2";  /* ROM 0x773fe8 */
static const char key_in_min_1[] = "ID_NOTIFICATION_IN_MIN_1";  /* ROM 0x773fcc */
static const char key_min_ago_2[] = "ID_NOTIFICATION_MIN_AGO_2";   /* ROM 0x774020 */
static const char key_min_ago_1[] = "ID_NOTIFICATION_MIN_AGO_1";   /* ROM 0x774004 */
static const char key_hour_ago_2[] = "ID_NOTIFICATION_HOUR_AGO_2"; /* ROM 0x774058 */
static const char key_hour_ago_1[] = "ID_NOTIFICATION_HOUR_AGO_1"; /* ROM 0x77403c */
static const char key_tomorrow[] = "ID_GENERAL_TOMORROW";   /* ROM 0x784838 */
static const char key_yesterday[] = "ID_GENERAL_YESTERDAY"; /* ROM 0x77d354 */
static const char fmt_relative[] = "%s %d%s";      /* ROM 0x78ed14 */
static const char fmt_time_12h[] = "%02d:%02d %s"; /* ROM 0x789dc0 */
static const char fmt_time_24h[] = "%02d:%02d";    /* ROM 0x78c854 */
static const char fmt_day_short[] = "%d/%d";       /* ROM 0x78ed1c */
static const char fmt_day_long[] = "%02d/%02d";    /* ROM 0x78c860 */

static const char fn_find_by_msg[] = "msg_tile_binding_find_by_msg";       /* ROM 0x767550 */
static const char fn_find_by_index[] = "msg_tile_binding_find_by_index";   /* ROM 0x767570 */
static const char fn_tile_by_msg_index[] = "msg_tile_index_find_by_msg_index"; /* ROM 0x75c42c */
static const char fn_msg_by_tile_index[] = "msg_index_find_by_tile_index";    /* ROM 0x7675b0 */
static const char fn_scroll_ready[] = "msg_notif_scroll_anim_ready_cb";   /* ROM 0x7675f0 */
static const char fn_bounce_ready[] = "msg_notif_bounce_transform_anim_ready_cb"; /* ROM 0x745f08 */
static const char fn_bounce[] = "msg_notif_execute_bounce_effect";        /* ROM 0x767610 */
static const char fn_scroll[] = "msg_notif_virtual_scroll_tileview";      /* ROM 0x75c450 */
static const char fn_jump[] = "msg_notif_jump_to_message_absolute";       /* ROM 0x75c474 */
static const char fn_delete_scroll[] = "msg_notif_delete_virtual_scroll_tileview"; /* ROM 0x745f34 */
static const char fn_delete_anim[] = "msg_notif_start_delete_animation";  /* ROM 0x75c4bc */
static const char fn_fade_complete[] = "msg_indicator_fade_complete_cb";  /* ROM 0x767630 */
static const char fn_add[] = "msg_notif_add_message";                     /* ROM 0x77d3b4 */
static const char fn_remove_current[] = "msg_notif_remove_current_message"; /* ROM 0x75c504 */
static const char fn_remove[] = "msg_notif_remove_message";               /* ROM 0x7740c8 */
static const char fn_hide[] = "msg_notif_hide_message";                   /* ROM 0x77d3cc */
static const char fn_create_content[] = "msg_notif_create_content_obj";   /* ROM 0x767690 */
static const char fn_create_item[] = "msg_notif_create_msg_item";         /* ROM 0x7740e4 */

static const char msg_node_null[] = "msg_node = %p, is NULL"; /* ROM 0x77d384 */
static const char msg_node_null_short[] = "[message_notify_list.ui]msg_node = %p, is NULL"; /* ROM 0x73a844 */
static const char msg_node_missing[] = "msg_node = %p, not found"; /* ROM 0x774074 */
static const char msg_node_missing_short[] =
    "[message_notify_list.ui]msg_node = %p, not found"; /* ROM 0x72fe5c */
static const char msg_index_range[] = "msg_index = %d, out of range"; /* ROM 0x767590 */
static const char msg_index_range_short[] =
    "[message_notify_list.ui]msg_index = %d, out of range"; /* ROM 0x725488 */
static const char msg_index_missing[] = "msg_index = %d, not found"; /* ROM 0x774090 */
static const char msg_index_missing_short[] =
    "[message_notify_list.ui]msg_index = %d, not found"; /* ROM 0x72fe90 */
static const char tile_index_range[] = "tile_index = %d, out of range"; /* ROM 0x7675d0 */
static const char tile_index_range_short[] =
    "[message_notify_list.ui]tile_index = %d, out of range"; /* ROM 0x7254c0 */
static const char tile_index_missing[] = "tile_index = %d, not found"; /* ROM 0x7740ac */
static const char tile_index_missing_short[] =
    "[message_notify_list.ui]tile_index = %d, not found"; /* ROM 0x72fec4 */
static const char scroll_done[] = "scroll_anim_ready_cb: scroll animation completed"; /* ROM 0x72fef8 */
static const char scroll_done_short[] =
    "[message_notify_list.ui]scroll_anim_ready_cb: scroll animation completed"; /* ROM 0x6f7370 */
static const char fifo_pop_failed[] = "scroll_anim_ready_cb: fifo_pop failed"; /* ROM 0x7508c4 */
static const char fifo_pop_failed_short[] =
    "[message_notify_list.ui]scroll_anim_ready_cb: fifo_pop failed"; /* ROM 0x711064 */
static const char bounce_back[] =
    "bounce_transform_anim_ready_cb, bouncing back to original position"; /* ROM 0x707c68 */
static const char bounce_back_short[] =
    "[message_notify_list.ui]bounce_transform_anim_ready_cb, bouncing back to original position"; /* ROM 0x6e1de4 */
static const char bounce_effect[] =
    "execute_bounce_effect: direction=%d, original_y=%d, target_y=%d"; /* ROM 0x7110a4 */
static const char bounce_effect_short[] =
    "[message_notify_list.ui]execute_bounce_effect: direction=%d, original_y=%d, target_y=%d"; /* ROM 0x6e58d0 */
static const char anim_busy[] = "animation in progress (state=%d), ignoring request"; /* ROM 0x72ff2c */
static const char anim_busy_short[] =
    "[message_notify_list.ui]animation in progress (state=%d), ignoring request"; /* ROM 0x6f73bc */
static const char no_messages[] = "no messages available"; /* ROM 0x77d39c */
static const char no_messages_short[] = "[message_notify_list.ui]no messages available"; /* ROM 0x73a874 */
static const char target_range[] = "invalid target index %d, must be 0-%d"; /* ROM 0x7508ec */
static const char target_range_short[] =
    "[message_notify_list.ui]invalid target index %d, must be 0-%d"; /* ROM 0x7110e4 */
static const char target_missing[] = "invalid target index %d, not found"; /* ROM 0x75c498 */
static const char target_missing_short[] =
    "[message_notify_list.ui]invalid target index %d, not found"; /* ROM 0x71a9bc */
static const char delete_missing[] = "delete_msg_index = %d, not found"; /* ROM 0x75c4e0 */
static const char delete_missing_short[] =
    "[message_notify_list.ui]delete_msg_index = %d, not found"; /* ROM 0x71a9f8 */
static const char remove_msg[] = "remove message: %d"; /* ROM 0x78484c */
static const char remove_msg_short[] = "[message_notify_list.ui]remove message: %d"; /* ROM 0x745f60 */
static const char binding_missing[] = "not found message binding: %p"; /* ROM 0x767650 */
static const char binding_missing_short[] =
    "[message_notify_list.ui]not found message binding: %p"; /* ROM 0x7254f8 */
static const char item_null[] = "msg_item is NULL for index %d"; /* ROM 0x767670 */
static const char item_null_short[] =
    "[message_notify_list.ui]msg_item is NULL for index %d"; /* ROM 0x725530 */
static const char content_null[] = "parent or content_obj is NULL"; /* ROM 0x7676b0 */
static const char content_null_short[] =
    "[message_notify_list.ui]parent or content_obj is NULL"; /* ROM 0x725568 */
static const char item_args_null[] = "tileview or msg_item is NULL"; /* ROM 0x7676d0 */
static const char item_args_null_short[] =
    "[message_notify_list.ui]tileview or msg_item is NULL"; /* ROM 0x7255a0 */
static const char tile_failed[] = "failed to create message object %d"; /* ROM 0x75c528 */
static const char tile_failed_short[] =
    "[message_notify_list.ui]failed to create message object %d"; /* ROM 0x71aa34 */
static const char content_failed[] = "failed to create content object for message %d"; /* ROM 0x73a8a4 */
static const char content_failed_short[] =
    "[message_notify_list.ui]failed to create content object for message %d"; /* ROM 0x6feb34 */
static const char text_app_name[] = "app_name"; /* ROM 0x78c86c */
static const char text_time[] = "time";         /* ROM 0x78ed24 */
static const char text_title[] = "title";       /* ROM 0x78ed2c */
static const char text_subtitle[] = "subtitle"; /* ROM 0x78c878 */
static const char text_detail[] = "detail";     /* ROM 0x78ed34 */
static const char text_empty[] = "";            /* ROM 0x551e54 (code literal) */

static int compact_log_enabled(void)
{
    return (audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u;
}

static const char *localized(const char *key)
{
    return audio_uart_page_45fffe(key, audio_uart_page_460084(key));
}

static const void *list_font(void)
{
    return (const void *)(uintptr_t)audio_system_alert_font_200746e0;
}

/* Split "YYYYMMDDTHHMMSS" into its six numeric fields. */
int32_t msg_notif_parse_iso_datetime_54fa56(const char *text, uint32_t *year, uint32_t *month,
                                            uint32_t *day, uint32_t *hour, uint32_t *minute,
                                            uint32_t *second)
{
    char copy[16];
    char field[8];

    if (text == NULL || g2_log_module_length(text) < 15u)
        return -1;
    (void)audio_settings_copy_text(copy, text, 15u);
    copy[15] = '\0';
    if (copy[8] != 'T')
        return -1;
    (void)audio_settings_copy_text(field, &copy[0], 4u);
    field[4] = '\0';
    *year = (uint32_t)atoi_48d868(field);
    (void)audio_settings_copy_text(field, &copy[4], 2u);
    field[2] = '\0';
    *month = (uint32_t)atoi_48d868(field);
    (void)audio_settings_copy_text(field, &copy[6], 2u);
    field[2] = '\0';
    *day = (uint32_t)atoi_48d868(field);
    (void)audio_settings_copy_text(field, &copy[9], 2u);
    field[2] = '\0';
    *hour = (uint32_t)atoi_48d868(field);
    (void)audio_settings_copy_text(field, &copy[11], 2u);
    field[2] = '\0';
    *minute = (uint32_t)atoi_48d868(field);
    (void)audio_settings_copy_text(field, &copy[13], 2u);
    field[2] = '\0';
    *second = (uint32_t)atoi_48d868(field);
    return 0;
}

/* Seconds from the message timestamp to now (negative for future stamps).
 * Stock passes the full year and leaves the other RTC words unset. */
int32_t msg_notif_time_diff_seconds_54fb46(const char *text, int32_t *diff)
{
    g2_rtc_time_t time;
    uint32_t message_epoch;

    if (msg_notif_parse_iso_datetime_54fa56(text, &time.year, &time.month, &time.day,
                                            &time.hour, &time.minute, &time.second) != 0)
        return -1;
    message_epoch = service_time_calendar_to_epoch_wrapper(&time);
    *diff = (int32_t)(service_time_current_epoch_get() - message_epoch);
    return 0;
}

static void format_clock(char *out, uint32_t size, int32_t hour, int32_t minute)
{
    if (audio_time_format_mode_46650c() == 1u) {
        int32_t hour12 = hour % 12;
        if (hour12 == 0)
            hour12 = 12;
        (void)g2_audio_dump_snprintf(out, size, fmt_time_12h, hour12, minute,
                                     hour < 12 ? am_text : pm_text);
    } else {
        (void)g2_audio_dump_snprintf(out, size, fmt_time_24h, hour, minute);
    }
}

static int date_format_month_first(void)
{
    return svc_universal_setting_get_date_format_466500() == 0u ||
           svc_universal_setting_get_date_format_466500() == 1u;
}

static void format_relative(char *out, uint32_t size, const char *key1, int32_t value,
                            const char *key2)
{
    const char *suffix = localized(key2);
    (void)g2_audio_dump_snprintf(out, size, fmt_relative, localized(key1), value, suffix);
}

/* Render a notification timestamp: now / N min ago / N h ago / clock time
 * today / yesterday / weekday within a week / month-day; future stamps give
 * now / in N min / clock / tomorrow / month-day. */
void msg_notif_format_time_54fb84(const char *text, char *out, uint32_t size)
{
    int32_t diff;
    uint32_t year, month, day, hour, minute, second;
    g2_rtc_time_t now;
    int32_t this_year;

    if (msg_notif_time_diff_seconds_54fb46(text, &diff) != 0 ||
        msg_notif_parse_iso_datetime_54fa56(text, &year, &month, &day, &hour, &minute,
                                            &second) != 0) {
        (void)g2_audio_dump_snprintf(out, size, fmt_s, text);
        return;
    }
    service_time_current_calendar_get(&now);
    this_year = (int32_t)now.year + 2000;

    if (diff < 0) {
        if (diff >= -59) {
            (void)g2_audio_dump_snprintf(out, size, localized(key_now));
        } else if (diff >= -3599) {
            format_relative(out, size, key_in_min_1, diff / -60, key_in_min_2);
        } else if ((int32_t)year == this_year && month == now.month && day == now.day) {
            format_clock(out, size, (int32_t)hour, (int32_t)minute);
        } else if ((int32_t)year == this_year && month == now.month && day == now.day + 1u) {
            (void)g2_audio_dump_snprintf(out, size, localized(key_tomorrow));
        } else if (date_format_month_first()) {
            (void)g2_audio_dump_snprintf(out, size, fmt_day_short, month, day);
        } else {
            (void)g2_audio_dump_snprintf(out, size, fmt_day_short, day, month);
        }
        return;
    }
    if (diff < 60) {
        (void)g2_audio_dump_snprintf(out, size, localized(key_now));
    } else if (diff < 3600) {
        format_relative(out, size, key_min_ago_1, diff / 60, key_min_ago_2);
    } else if (diff < 10800) {
        format_relative(out, size, key_hour_ago_1, diff / 3600, key_hour_ago_2);
    } else if ((int32_t)year == this_year && month == now.month && day == now.day) {
        format_clock(out, size, (int32_t)hour, (int32_t)minute);
    } else if ((int32_t)year == this_year && month == now.month && day == now.day - 1u) {
        (void)g2_audio_dump_snprintf(out, size, localized(key_yesterday));
    } else if (diff < 604800) {
        uint32_t weekday = rtc_weekday_from_date_4d3cf8(year, month, day);
        if (weekday < 7u)
            (void)g2_audio_dump_snprintf(out, size, fmt_s,
                                         localized(g2_msg_notif_weekday_keys_2000425c[weekday]));
        else if (date_format_month_first())
            (void)g2_audio_dump_snprintf(out, size, fmt_day_long, month, day);
        else
            (void)g2_audio_dump_snprintf(out, size, fmt_day_long, day, month);
    } else if (date_format_month_first()) {
        (void)g2_audio_dump_snprintf(out, size, fmt_day_long, month, day);
    } else {
        (void)g2_audio_dump_snprintf(out, size, fmt_day_long, day, month);
    }
}

/* Stock keeps two identical clear routines (0x54ff36 / 0x54ff48). */
void msg_tile_binding_init_54ff36(void)
{
    (void)aeabi_memset_43c0e4(g2_msg_tile_bindings_20071db8, sizeof g2_msg_tile_bindings_20071db8, 0);
}

void msg_tile_binding_clear_54ff48(void)
{
    (void)aeabi_memset_43c0e4(g2_msg_tile_bindings_20071db8, sizeof g2_msg_tile_bindings_20071db8, 0);
}

void msg_tile_binding_add_54ff64(void *tile, g2_ancc_record_t *msg, uint8_t msg_index,
                                 uint8_t tile_index)
{
    g2_msg_tile_binding_t *row;

    if (tile == NULL || msg == NULL || tile_index >= MSG_NOTIF_MAX_BINDINGS)
        return;
    row = &g2_msg_tile_bindings_20071db8[tile_index];
    row->tile = tile;
    row->msg = msg;
    row->msg_index = msg_index;
    row->tile_index = tile_index;
    row->valid = 1u;
}

g2_msg_tile_binding_t *msg_tile_binding_find_by_msg_54ffb4(const g2_ancc_record_t *msg)
{
    if (msg == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_find_by_msg, 0x1c5u, msg_node_null, msg);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, msg_node_null_short, msg_node_null_short, msg);
        return NULL;
    }
    for (int32_t i = 0; i < MSG_NOTIF_MAX_BINDINGS; i++) {
        g2_msg_tile_binding_t *row = &g2_msg_tile_bindings_20071db8[i];
        if (row->valid != 0u && row->msg == msg)
            return row;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, fn_find_by_msg, 0x1ceu, msg_node_missing, msg);
    if (compact_log_enabled())
        (void)compress_log_output(0x08400000u, msg_node_missing_short, msg_node_missing_short, msg);
    return NULL;
}

g2_msg_tile_binding_t *msg_tile_binding_find_by_index_550086(uint8_t msg_index)
{
    if (msg_index >= MSG_NOTIF_MAX_BINDINGS) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_find_by_index, 0x1d5u, msg_index_range,
                               (uint32_t)msg_index);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, msg_index_range_short, msg_index_range_short,
                                      (uint32_t)msg_index);
        return NULL;
    }
    for (int32_t i = 0; i < MSG_NOTIF_MAX_BINDINGS; i++) {
        g2_msg_tile_binding_t *row = &g2_msg_tile_bindings_20071db8[i];
        if (row->valid != 0u && row->msg_index == msg_index)
            return row;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, fn_find_by_index, 0x1deu, msg_index_missing,
                           (uint32_t)msg_index);
    if (compact_log_enabled())
        (void)compress_log_output(0x08400000u, msg_index_missing_short, msg_index_missing_short,
                                  (uint32_t)msg_index);
    return NULL;
}

int16_t msg_tile_index_find_by_msg_index_550170(uint8_t msg_index)
{
    if (msg_index >= MSG_NOTIF_MAX_BINDINGS) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_tile_by_msg_index, 0x1e5u, msg_index_range,
                               (uint32_t)msg_index);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, msg_index_range_short, msg_index_range_short,
                                      (uint32_t)msg_index);
        return -1;
    }
    for (int32_t i = 0; i < MSG_NOTIF_MAX_BINDINGS; i++) {
        const g2_msg_tile_binding_t *row = &g2_msg_tile_bindings_20071db8[i];
        if (row->valid != 0u && row->msg_index == msg_index)
            return (int16_t)row->tile_index;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, fn_tile_by_msg_index, 0x1eeu, msg_index_missing,
                           (uint32_t)msg_index);
    if (compact_log_enabled())
        (void)compress_log_output(0x08400000u, msg_index_missing_short, msg_index_missing_short,
                                  (uint32_t)msg_index);
    return -1;
}

/* Only the three visible tiles are valid lookups here. */
int16_t msg_index_find_by_tile_index_55025c(uint8_t tile_index)
{
    if (tile_index >= MSG_NOTIF_VISIBLE_DOTS) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_msg_by_tile_index, 0x1f5u, tile_index_range,
                               (uint32_t)tile_index);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, tile_index_range_short, tile_index_range_short,
                                      (uint32_t)tile_index);
        return -1;
    }
    if (g2_msg_tile_bindings_20071db8[tile_index].valid == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_msg_by_tile_index, 0x1fdu, tile_index_missing,
                               (uint32_t)tile_index);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, tile_index_missing_short,
                                      tile_index_missing_short, (uint32_t)tile_index);
        return -1;
    }
    return (int16_t)g2_msg_tile_bindings_20071db8[tile_index].msg_index;
}

static void send_page_record(uint8_t code, uint8_t value)
{
    uint8_t record[6] = { PAGE_RECORD_INPUT, code, value, 0u, 0u, 0u };
    audio_uart_master_display_refresh(MSG_NOTIF_APP_ID, record, sizeof record, 0u);
}

/* Forward an input to the master arm; scrolls are dropped while animating. */
uint32_t msg_notif_input_forward_550334(uint32_t code, const void *event)
{
    (void)event;
    if (code == INPUT_CLICK) {
        send_page_record(INPUT_CLICK, 0u);
    } else if (code == INPUT_CLOSE) {
        send_page_record(INPUT_CLOSE, 0u);
    } else if (code == INPUT_SCROLL_DOWN) {
        if (g2_msg_notif_anim_busy != 0u)
            return 0u;
        if (g2_msg_notif_current_index_20074cd0 < 1)
            g2_msg_notif_current_index_20074cd0 = 0;
        send_page_record(INPUT_SCROLL_DOWN, 1u);
    } else if (code == INPUT_SCROLL_UP) {
        if (g2_msg_notif_anim_busy != 0u)
            return 0u;
        if (msg_notif_last_index_5511bc() < g2_msg_notif_current_index_20074cd0)
            g2_msg_notif_current_index_20074cd0 = msg_notif_last_index_5511bc();
        send_page_record(INPUT_SCROLL_UP, 1u);
    }
    return 0u;
}

/* Tileview scroll finished: settle a pending delete, refresh, then replay one
 * queued page record. */
void msg_notif_scroll_anim_ready_cb_550432(void *anim)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    g2_ui_fifo_t *fifo;
    uint8_t record[10];

    (void)anim;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_scroll_ready, 0x2a1u, scroll_done);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c000000u, scroll_done_short, scroll_done_short);
    if (g2_msg_notif_delete_tile_20004554 >= 0) {
        audio_uart_display_audio_reset_441488(ui->items[g2_msg_notif_delete_tile_20004554].tile,
                                              0xffu, 0u);
        message_notify_ui_reflash_551ed8(ui->tileview, 2u);
        g2_msg_notif_delete_tile_20004554 = -1;
        g2_msg_notif_delete_count_20004555 = -1;
        g2_msg_notif_delete_visible_20004556 = -1;
    } else {
        message_notify_ui_reflash_551ed8(ui->tileview, 3u);
    }
    g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_IDLE;

    fifo = (g2_ui_fifo_t *)g2_msg_notif_event_fifo;
    if (fifo == NULL || ui_common_api_fn_00509dfa(fifo) != 0)
        return;
    (void)aeabi_memset_43c0e4(record, sizeof record, 0);
    if (ui_common_api_fn_00509e14(fifo, record, 6u) < 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_scroll_ready, 0x2ecu, fifo_pop_failed);
        if (compact_log_enabled())
            (void)compress_log_output(0x08000000u, fifo_pop_failed_short, fifo_pop_failed_short);
        return;
    }
    if (record[0] == PAGE_RECORD_INPUT) {
        switch (record[1]) {
        case INPUT_CLICK:
            msg_notif_remove_current_message_551240();
            break;
        case INPUT_SCROLL_UP:
            msg_notif_virtual_scroll_tileview_550820(1);
            break;
        case INPUT_SCROLL_DOWN:
            msg_notif_virtual_scroll_tileview_550820(-1);
            break;
        case INPUT_JUMP:
            msg_notif_jump_to_message_absolute_550968(record[2]);
            break;
        case INPUT_CLOSE:
            if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
                audio_system_alert_close_464c36(4u, 0u, 0u, 0u);
            break;
        default:
            break;
        }
    } else if (record[0] == PAGE_RECORD_BASICINFO) {
        if (record[1] == 1u)
            msg_notif_add_message_5511ce(g2_msg_notif_page);
    }
}

/* lv_anim exec/ready trampolines (no inventory rows). */
void msg_notif_scroll_y_exec_cb_5505d0(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void msg_notif_set_y_exec_cb_5505da(void *obj, int32_t y)
{
    audio_uart_page_43f142(obj, y);
}

void msg_notif_bounce_back_ready_cb_5505e2(void *anim)
{
    msg_notif_scroll_anim_ready_cb_550432(anim);
}

/* Bounce reached its offset: animate the tileview back to the saved y. */
void msg_notif_bounce_transform_anim_ready_cb_5505ea(void *anim)
{
    g2_lv_anim_t a;
    void *tileview;

    (void)anim;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_bounce_ready, 0x30cu, bounce_back);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c000000u, bounce_back_short, bounce_back_short);
    audio_uart_lv_anim_init_4503d6(&a);
    tileview = g2_msg_notif_ui_2006f734.tileview;
    a.var = tileview;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_43fce0(tileview),
                                     g2_msg_notif_original_y_20074cd4);
    a.duration = g2_msg_notif_bounce_duration_20004280;
    a.exec_cb = msg_notif_set_y_exec_cb_5505da;
    a.path_cb = audio_uart_lv_anim_path_45065a;
    a.completed_cb = msg_notif_bounce_back_ready_cb_5505e2;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void msg_notif_start_scroll_anim_550694(void *obj, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t a;

    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(obj), target_y);
    a.duration = duration;
    a.exec_cb = msg_notif_scroll_y_exec_cb_5505d0;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = msg_notif_scroll_anim_ready_cb_550432;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Past either end of the list: nudge the tileview by the bounce distance. */
void msg_notif_execute_bounce_effect_550708(int32_t direction)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    g2_lv_anim_t a;
    int32_t target;

    if (ui->tileview == NULL)
        return;
    audio_uart_page_43f66c(ui->tileview);
    g2_msg_notif_original_y_20074cd4 = audio_uart_lv_obj_y_43fce0(ui->tileview);
    if (direction == 1 && msg_notif_last_index_5511bc() <= g2_msg_notif_current_index_20074cd0)
        target = g2_msg_notif_original_y_20074cd4 - g2_msg_notif_bounce_distance_2000427c;
    else if (direction == -1 && g2_msg_notif_current_index_20074cd0 < 1)
        target = g2_msg_notif_bounce_distance_2000427c + g2_msg_notif_original_y_20074cd4;
    else
        return;
    g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_BOUNCE;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_bounce, 0x340u, bounce_effect, direction,
                           g2_msg_notif_original_y_20074cd4, target);
    if (compact_log_enabled())
        (void)compress_log_output(0x0cc00000u, bounce_effect_short, bounce_effect_short, direction,
                                  g2_msg_notif_original_y_20074cd4, target);
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = ui->tileview;
    audio_uart_lv_anim_values_4506ce(&a, g2_msg_notif_original_y_20074cd4, target);
    a.duration = g2_msg_notif_bounce_duration_20004280;
    a.exec_cb = msg_notif_set_y_exec_cb_5505da;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = msg_notif_bounce_transform_anim_ready_cb_5505ea;
    (void)audio_uart_lv_anim_start_450408(&a);
}

static void log_anim_busy(uint8_t level, const char *function, uint32_t line, uint32_t mask)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, path, function, line, anim_busy,
                           (uint32_t)g2_msg_notif_anim_busy);
    if (compact_log_enabled())
        (void)compress_log_output(mask, anim_busy_short, anim_busy_short,
                                  (uint32_t)g2_msg_notif_anim_busy);
}

void msg_notif_virtual_scroll_tileview_550820(int32_t direction)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    int32_t count;
    int16_t tile;

    if (ui->tileview == NULL)
        return;
    if (g2_msg_notif_anim_busy != 0u) {
        log_anim_busy(3u, fn_scroll, 0x355u, 0x0c400000u);
        return;
    }
    (void)audio_uart_lv_obj_y_44e498(ui->tileview);
    count = (int32_t)audio_settings_unread_message_count();
    if (count == 0) {
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_IDLE;
        return;
    }
    if (direction == 1 && g2_msg_notif_current_index_20074cd0 < count - 1) {
        g2_msg_notif_current_index_20074cd0++;
    } else if (direction == -1 && g2_msg_notif_current_index_20074cd0 >= 1) {
        g2_msg_notif_current_index_20074cd0--;
    } else {
        msg_notif_execute_bounce_effect_550708(direction);
        return;
    }
    tile = msg_tile_index_find_by_msg_index_550170((uint8_t)g2_msg_notif_current_index_20074cd0);
    if (tile >= 0) {
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_SCROLL;
        msg_notif_start_scroll_anim_550694(ui->tileview, MSG_NOTIF_TILE_HEIGHT * tile,
                                           g2_msg_notif_scroll_duration_20004278);
    }
    msg_indicator_update_550e2e(g2_msg_notif_current_index_20074cd0, 1u);
}

/* Jump to a message index; the duration grows 50 ms per skipped tile. */
void msg_notif_jump_to_message_absolute_550968(uint32_t index)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    int32_t target = (int32_t)index;
    int32_t count;
    int16_t current_tile;
    int16_t target_tile;
    int32_t duration;

    if (ui->tileview == NULL)
        return;
    count = (int32_t)audio_settings_unread_message_count();
    if (count == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_jump, 0x399u, no_messages);
        if (compact_log_enabled())
            (void)compress_log_output(0x08000000u, no_messages_short, no_messages_short);
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_IDLE;
        return;
    }
    if (target < 0 || target >= count) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_jump, 0x3a0u, target_range, target, count - 1);
        if (compact_log_enabled())
            (void)compress_log_output(0x08800000u, target_range_short, target_range_short, target,
                                      count - 1);
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_IDLE;
        return;
    }
    current_tile = msg_tile_index_find_by_msg_index_550170((uint8_t)g2_msg_notif_current_index_20074cd0);
    target_tile = msg_tile_index_find_by_msg_index_550170((uint8_t)target);
    if (target_tile < 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_jump, 0x3a8u, target_missing, target);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, target_missing_short, target_missing_short,
                                      target);
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_IDLE;
        return;
    }
    g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_SCROLL;
    duration = (iar_abs_509694((int32_t)target_tile - (int32_t)current_tile) - 1) * 50 +
               g2_msg_notif_scroll_duration_20004278;
    if ((int32_t)target_tile == g2_msg_notif_current_index_20074cd0) {
        duration = 10;
    } else {
        g2_msg_notif_current_index_20074cd0 = target_tile;
        msg_indicator_update_550e2e(g2_msg_notif_current_index_20074cd0, 1u);
    }
    msg_notif_start_scroll_anim_550694(ui->tileview, MSG_NOTIF_TILE_HEIGHT * target_tile, duration);
}

/* After a delete fade: slide one tile over the removed slot. */
void msg_notif_delete_virtual_scroll_tileview_550b14(int32_t direction)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    int32_t y;
    int8_t count;
    int8_t visible;
    int8_t deleted;

    if (ui->tileview == NULL)
        return;
    if (g2_msg_notif_anim_busy != MSG_NOTIF_ANIM_IDLE &&
        g2_msg_notif_anim_busy != MSG_NOTIF_ANIM_DELETE) {
        log_anim_busy(3u, fn_delete_scroll, 0x3ceu, 0x0c400000u);
        return;
    }
    y = audio_uart_lv_obj_y_44e498(ui->tileview);
    count = g2_msg_notif_delete_count_20004555;
    visible = g2_msg_notif_delete_visible_20004556;
    deleted = g2_msg_notif_delete_tile_20004554;
    if (count == 0 || visible == 0)
        return;
    if (direction == 1 && deleted < visible - 1) {
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_SCROLL;
        msg_notif_start_scroll_anim_550694(ui->tileview, MSG_NOTIF_TILE_HEIGHT + y,
                                           g2_msg_notif_scroll_duration_20004278);
    } else if (direction == -1 && deleted >= 1) {
        g2_msg_notif_current_index_20074cd0--;
        g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_SCROLL;
        msg_notif_start_scroll_anim_550694(ui->tileview, y - MSG_NOTIF_TILE_HEIGHT,
                                           g2_msg_notif_scroll_duration_20004278);
    }
}

void msg_notif_opa_exec_cb_550bf4(void *obj, int32_t opa)
{
    if (obj != NULL)
        audio_uart_display_audio_reset_441488(obj, (uint8_t)opa, 0u);
}

void msg_notif_delete_anim_ready_cb_550cc4(void *anim);

void msg_notif_start_delete_animation_550c04(void *tile, uint8_t msg_index)
{
    g2_lv_anim_t a;

    if (tile == NULL)
        return;
    if (g2_msg_notif_anim_busy != MSG_NOTIF_ANIM_IDLE) {
        log_anim_busy(2u, fn_delete_anim, 0x459u, 0x08400000u);
        return;
    }
    g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_DELETE;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = tile;
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = 250;
    a.exec_cb = msg_notif_opa_exec_cb_550bf4;
    a.path_cb = audio_uart_lv_anim_default_path_450634;
    a.completed_cb = msg_notif_delete_anim_ready_cb_550cc4;
    (void)audio_uart_lv_anim_start_450408(&a);
    msg_indicator_fade_out_550f8c(msg_index);
}

/* Delete fade finished: close the gap, rebuild if messages arrived meanwhile,
 * or leave the page when the list emptied (master arm only). */
void msg_notif_delete_anim_ready_cb_550cc4(void *anim)
{
    if (g2_msg_notif_delete_tile_20004554 < g2_msg_notif_delete_visible_20004556 - 1)
        msg_notif_delete_virtual_scroll_tileview_550b14(1);
    else if (g2_msg_notif_delete_tile_20004554 >= 1)
        msg_notif_delete_virtual_scroll_tileview_550b14(-1);
    else if ((int16_t)g2_msg_notif_delete_count_20004555 <
             (int16_t)(uint8_t)audio_settings_unread_message_count())
        message_notify_ui_reflash_551ed8(g2_msg_notif_ui_2006f734.tileview, 1u);
    else if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
        audio_system_alert_close_464c36(4u, 0u, 0u, 0u);
    msg_indicator_fade_complete_cb_551018(anim);
}

/* Lay out `count` dots, centred in the 28 px window when fewer than three. */
void msg_indicator_layout_550d3c(uint8_t count)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    int32_t total;
    int32_t offset;

    if (ui->indicator == NULL)
        return;
    for (uint8_t i = 0u; i < MSG_NOTIF_MAX_DOTS; i++)
        if (ui->dots[i] != NULL)
            audio_uart_page_43ded4(ui->dots[i], LV_OBJ_FLAG_HIDDEN);
    if (count > MSG_NOTIF_MAX_DOTS)
        count = MSG_NOTIF_MAX_DOTS;
    total = count != 0u ? ((int32_t)count - 1) * 8 + (int32_t)count * 4 : 0;
    offset = 0;
    if (count != 0u && count < 3u) {
        offset = (28 - total) / 2;
        if (offset < 0)
            offset = 0;
    }
    for (uint8_t i = 0u; i < count; i++) {
        void *dot = ui->dots[i];
        if (dot == NULL)
            continue;
        audio_uart_page_43dfa4(dot, LV_OBJ_FLAG_HIDDEN);
        audio_uart_page_44127e(dot, audio_uart_page_44104c(COLOR_DIM), 0u);
        audio_uart_page_43f6b8(dot, 13u, 0, MSG_NOTIF_DOT_STEP * (int32_t)i + offset);
        audio_uart_display_audio_reset_441488(dot, 0xffu, 0u);
    }
    audio_uart_lv_scroll_to_y_44ea04(ui->indicator, 0, 0u);
}

void msg_indicator_update_550e2e(int32_t index, uint8_t animate)
{
    int32_t count = (int32_t)audio_settings_unread_message_count();

    if (count < 1)
        return;
    if (index < 0)
        index = 0;
    if (index >= count)
        index = count - 1;
    for (int32_t i = 0; i < count && i < MSG_NOTIF_MAX_DOTS; i++) {
        void *dot = g2_msg_notif_ui_2006f734.dots[i];
        if (dot == NULL)
            continue;
        if (i == index)
            audio_uart_page_44127e(dot, audio_uart_page_44104c(COLOR_WHITE), 0u);
        else
            audio_uart_page_44127e(dot, audio_uart_page_44104c(COLOR_DIM), 0u);
    }
    if (animate != 0u)
        msg_indicator_scroll_to_550eda(index, 200u, 0);
    else
        msg_indicator_scroll_to_550eda(index, 0u, 0);
}

void msg_indicator_scroll_y_exec_cb_550ed0(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

void msg_indicator_scroll_to_550eda(int32_t index, uint32_t duration, int32_t direction)
{
    msg_indicator_scroll_anim_550ef4((uint8_t)audio_settings_unread_message_count(), index,
                                     duration, direction);
}

/* Keep the selected dot inside the three-dot window. */
void msg_indicator_scroll_anim_550ef4(int32_t count, int32_t index, uint32_t duration,
                                      int32_t direction)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    g2_lv_anim_t a;
    int32_t first;

    (void)direction;
    if (ui->indicator == NULL || count < 1)
        return;
    if (count <= MSG_NOTIF_VISIBLE_DOTS) {
        audio_uart_lv_scroll_to_y_44ea04(ui->indicator, 0, 0u);
        return;
    }
    if (index < 1)
        first = 0;
    else if (index >= count - 1)
        first = count - MSG_NOTIF_VISIBLE_DOTS;
    else
        first = index - 1;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = ui->indicator;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(ui->indicator),
                                     first * (8 + 4));
    a.duration = (int32_t)duration;
    a.exec_cb = msg_indicator_scroll_y_exec_cb_550ed0;
    a.path_cb = audio_uart_lv_anim_path_450688;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void msg_indicator_fade_out_550f8c(uint8_t index)
{
    g2_lv_anim_t a;
    void *dot;

    if (index >= MSG_NOTIF_MAX_DOTS)
        return;
    dot = g2_msg_notif_ui_2006f734.dots[index];
    if (dot == NULL || audio_uart_lv_obj_has_flag_43e0e0(dot, LV_OBJ_FLAG_HIDDEN) != 0u)
        return;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = dot;
    audio_uart_lv_anim_values_4506ce(&a, 0xff, 0);
    a.duration = 200;
    a.exec_cb = msg_notif_opa_exec_cb_550bf4;
    a.path_cb = audio_uart_lv_anim_default_path_450634;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Re-lay the dots after a delete and pick the dot that becomes selected; with
 * three or more left, the edge marker is pinned to the window side the list
 * moves towards. */
void msg_indicator_fade_complete_cb_551018(void *anim)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    int8_t count = g2_msg_notif_delete_count_20004555;
    int8_t remain;
    int16_t deleted;
    int8_t target;
    int8_t direction;
    int8_t before;
    int8_t after;

    (void)anim;
    if (count < 1)
        return;
    remain = (int8_t)(count - 1);
    deleted = msg_index_find_by_tile_index_55025c((uint8_t)g2_msg_notif_delete_tile_20004554);
    if (deleted < 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_fade_complete, 0x534u, delete_missing,
                               (int32_t)g2_msg_notif_delete_tile_20004554);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, delete_missing_short, delete_missing_short,
                                      (int32_t)g2_msg_notif_delete_tile_20004554);
        return;
    }
    target = deleted < remain - 1 ? (int8_t)(deleted + 1) : (int8_t)(remain - 1);
    if (remain < 3)
        target = (int8_t)deleted;
    direction = 1;
    before = (int8_t)deleted;
    after = (int8_t)(count - deleted - 1);
    if (remain < 3) {
        msg_indicator_layout_550d3c((uint8_t)remain);
        msg_indicator_update_550e2e(target, 0u);
        return;
    }
    if (before == 0 && after >= 3) {
        direction = 1;
        target = (int8_t)(deleted + 2);
    } else if (before == 1 && after >= 2) {
        direction = 1;
        target = (int8_t)(deleted + 1);
    } else if (before >= 2 && after == 1) {
        direction = -1;
        target = (int8_t)(deleted - 1);
    } else if (before >= 3 && after == 0) {
        direction = -1;
        target = (int8_t)(deleted - 2);
    }
    if (before != 0 && after != 0) {
        if (direction == -1) {
            audio_uart_page_43dfa4(ui->indicator_edge, LV_OBJ_FLAG_HIDDEN);
            audio_uart_page_43f09a(ui->indicator_edge, 0, 0);
            audio_uart_page_43f6d6(ui->indicator_edge, ui->indicator, 4u, 0, 0);
        } else if (direction == 1) {
            audio_uart_page_43dfa4(ui->indicator_edge, LV_OBJ_FLAG_HIDDEN);
            audio_uart_page_43f09a(ui->indicator_edge, 0, 0);
            audio_uart_page_43f6d6(ui->indicator_edge, ui->indicator, 1u, 0, 0);
        }
    }
    msg_indicator_scroll_anim_550ef4(count, target, 200u, direction);
}

int32_t msg_notif_last_index_5511bc(void)
{
    int32_t count = (int32_t)audio_settings_unread_message_count();
    return count < 1 ? 0 : count - 1;
}

void msg_notif_add_message_5511ce(void *page)
{
    if (page == NULL)
        return;
    if (g2_msg_notif_anim_busy != MSG_NOTIF_ANIM_IDLE) {
        log_anim_busy(2u, fn_add, 0x581u, 0x08400000u);
        return;
    }
    g2_msg_notif_anim_busy = MSG_NOTIF_ANIM_ADD;
    message_notify_ui_reflash_551ed8(page, 1u);
}

void msg_notif_remove_current_message_551240(void)
{
    g2_msg_tile_binding_t *row =
        msg_tile_binding_find_by_index_550086((uint8_t)g2_msg_notif_current_index_20074cd0);

    if (row == NULL || row->valid == 0u)
        return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, fn_remove_current, 0x58eu, remove_msg,
                           (uint32_t)row->msg_index);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c400000u, remove_msg_short, remove_msg_short,
                                  (uint32_t)row->msg_index);
    msg_notif_remove_message_5512b0(row->msg);
}

void msg_notif_remove_message_5512b0(g2_ancc_record_t *msg)
{
    if (g2_msg_notif_anim_busy == MSG_NOTIF_ANIM_IDLE)
        msg_notif_hide_message_55131c(msg);
    else
        log_anim_busy(2u, fn_remove, 0x598u, 0x08400000u);
}

/* Record the delete, drop the ANCC record and fade its tile out. */
void msg_notif_hide_message_55131c(g2_ancc_record_t *msg)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;
    g2_msg_tile_binding_t *row;
    g2_msg_notif_item_t *item;

    if (ui->tileview == NULL)
        return;
    row = msg_tile_binding_find_by_msg_54ffb4(msg);
    if (row == NULL || row->valid == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_hide, 0x5aau, binding_missing, msg);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, binding_missing_short, binding_missing_short, msg);
        return;
    }
    item = &ui->items[row->tile_index];
    if (item->tile == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, fn_hide, 0x5b1u, item_null,
                               (uint32_t)row->tile_index);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, item_null_short, item_null_short,
                                      (uint32_t)row->tile_index);
        return;
    }
    g2_msg_notif_delete_tile_20004554 = (int8_t)row->tile_index;
    g2_msg_notif_delete_count_20004555 = (int8_t)audio_settings_unread_message_count();
    if (g2_msg_notif_delete_count_20004555 >= 4)
        g2_msg_notif_delete_visible_20004556 = MSG_NOTIF_VISIBLE_DOTS;
    else
        g2_msg_notif_delete_visible_20004556 = g2_msg_notif_delete_count_20004555;
    service_ancc_record_remove(msg);
    msg_notif_start_delete_animation_550c04(item->tile, row->msg_index);
}

void msg_notif_empty_show_55141c(void)
{
    if (g2_msg_notif_ui_2006f734.empty_label != NULL)
        audio_uart_page_43dfa4(g2_msg_notif_ui_2006f734.empty_label, LV_OBJ_FLAG_HIDDEN);
}

void msg_notif_empty_hide_551432(void)
{
    if (g2_msg_notif_ui_2006f734.empty_label != NULL)
        audio_uart_page_43ded4(g2_msg_notif_ui_2006f734.empty_label, LV_OBJ_FLAG_HIDDEN);
}

void msg_notif_tileview_show_551448(void)
{
    if (g2_msg_notif_ui_2006f734.tileview != NULL)
        audio_uart_page_43dfa4(g2_msg_notif_ui_2006f734.tileview, LV_OBJ_FLAG_HIDDEN);
}

void msg_notif_tileview_hide_551464(void)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;

    if (ui->tileview != NULL)
        audio_uart_page_43ded4(ui->tileview, LV_OBJ_FLAG_HIDDEN);
    if (ui->indicator_edge != NULL)
        audio_uart_page_43ded4(ui->indicator_edge, LV_OBJ_FLAG_HIDDEN);
}

void msg_indicator_show_551494(void)
{
    g2_msg_notif_ui_t *ui = &g2_msg_notif_ui_2006f734;

    if (ui->indicator != NULL)
        audio_uart_page_43dfa4(ui->indicator, LV_OBJ_FLAG_HIDDEN);
    if (ui->indicator_edge != NULL)
        audio_uart_page_43ded4(ui->indicator_edge, LV_OBJ_FLAG_HIDDEN);
}

void msg_indicator_hide_5514bc(void)
{
    if (g2_msg_notif_ui_2006f734.indicator != NULL)
        audio_uart_page_43ded4(g2_msg_notif_ui_2006f734.indicator, LV_OBJ_FLAG_HIDDEN);
}

static void *create_text_label(void *parent, int32_t width)
{
    void *label = audio_uart_page_499416(parent);
    audio_uart_page_43f506(label, width);
    audio_uart_page_43f568(label, 0x1e);
    return label;
}

static void style_text_label(void *label, uint32_t color)
{
    audio_uart_page_44140e(label, audio_uart_page_44104c(color), 0u);
    audio_uart_page_44143e(label, list_font(), 0u);
}

static void clear_box(void *obj)
{
    audio_uart_page_44131c(obj, 0, 0u);
    lv_obj_set_style_pad_all_54fa24(obj, 0, 0u);
}

/* Build the card text column: app name / time on the first row, title,
 * separator and subtitle on the second, message body below. */
g2_msg_notif_content_t *msg_notif_create_content_obj_5514f0(void *parent,
                                                            g2_msg_notif_content_t *content)
{
    if (parent == NULL || content == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, fn_create_content, 0x642u, content_null);
        if (compact_log_enabled())
            (void)compress_log_output(0x04000000u, content_null_short, content_null_short);
        return NULL;
    }
    (void)aeabi_memset_43c0e4(content, sizeof *content, 0);

    content->obj = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(content->obj, 0x1d9);
    audio_uart_page_43f568(content->obj, LV_SIZE_CONTENT_FORK);
    audio_uart_page_4411aa(content->obj, 0xa6, 0u);
    audio_uart_page_43f09a(content->obj, 0x2e, 0);
    clear_box(content->obj);
    audio_uart_page_44127e(content->obj, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(content->obj, 0xffu, 0u);
    audio_uart_page_43dfa4(content->obj, LV_OBJ_FLAG_CLICKABLE_SCROLLABLE);

    content->app_name = create_text_label(content->obj, 0x15b);
    audio_uart_page_43f6b8(content->app_name, 1u, 0, 0);
    style_text_label(content->app_name, COLOR_WHITE);
    clear_box(content->app_name);
    audio_uart_page_layout_499678(content->app_name, 1u);
    audio_uart_page_49942e(content->app_name, text_app_name);

    content->time = create_text_label(content->obj, 0x6e);
    audio_uart_page_43f6b8(content->time, 3u, 0, 0);
    style_text_label(content->time, COLOR_DIM);
    audio_uart_page_44145a(content->time, 3u, 0u);
    clear_box(content->time);
    audio_uart_page_49942e(content->time, text_time);

    content->title = create_text_label(content->obj, LV_SIZE_CONTENT_FORK);
    audio_uart_page_43f6d6(content->title, content->app_name, 13u, 0, 12);
    style_text_label(content->title, COLOR_WHITE);
    clear_box(content->title);
    audio_uart_page_layout_499678(content->title, 1u);
    audio_uart_page_49942e(content->title, text_title);

    content->separator = audio_uart_page_498668(content->obj);
    audio_uart_page_43f4c0(content->separator, 0x18, 0x18);
    audio_uart_page_498680(content->separator, g2_msg_notif_separator_icon_76e248);
    audio_uart_page_43f6d6(content->separator, content->title, 0x14u, 0, 0);

    content->subtitle = create_text_label(content->obj, LV_SIZE_CONTENT_FORK);
    audio_uart_page_43f6d6(content->subtitle, content->separator, 0x14u, 0, 0);
    style_text_label(content->subtitle, COLOR_WHITE);
    clear_box(content->subtitle);
    audio_uart_page_layout_499678(content->subtitle, 1u);
    audio_uart_page_49942e(content->subtitle, text_subtitle);

    content->detail = audio_uart_page_499416(content->obj);
    audio_uart_page_43f506(content->detail, 0x1d9);
    audio_uart_page_layout_499678(content->detail, 0u);
    audio_uart_page_43f568(content->detail, LV_SIZE_CONTENT_FORK);
    audio_uart_page_43f6d6(content->detail, content->title, 13u, 0, 4);
    style_text_label(content->detail, COLOR_WHITE);
    clear_box(content->detail);
    audio_uart_page_49942e(content->detail, text_detail);
    return content;
}

/* Add tile `index` to the tileview and build its bordered card. */
g2_msg_notif_item_t *msg_notif_create_msg_item_551814(void *tileview, uint8_t index,
                                                      g2_msg_notif_item_t *item)
{
    void *previous;

    if (tileview == NULL || item == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, fn_create_item, 0x6c0u, item_args_null);
        if (compact_log_enabled())
            (void)compress_log_output(0x04000000u, item_args_null_short, item_args_null_short);
        return NULL;
    }
    (void)aeabi_memset_43c0e4(item, sizeof *item, 0);
    item->tile = lv_tileview_add_tile_50ff0e(tileview, 0u, index, LV_DIR_VER);
    if (item->tile == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, fn_create_item, 0x6cau, tile_failed,
                               (uint32_t)index);
        if (compact_log_enabled())
            (void)compress_log_output(0x04400000u, tile_failed_short, tile_failed_short,
                                      (uint32_t)index);
        return NULL;
    }
    audio_uart_page_43f506(item->tile, 0x224);
    audio_uart_page_43f568(item->tile, MSG_NOTIF_TILE_HEIGHT);
    if (index == 0u) {
        audio_uart_page_43f6b8(item->tile, 1u, 0, 0);
    } else {
        previous = audio_uart_lv_child_get_44dce2(tileview, (int32_t)index - 1);
        if (previous == NULL)
            audio_uart_page_43f6b8(item->tile, 1u, 0, 0);
        else
            audio_uart_page_43f6d6(item->tile, previous, 13u, 0, 0);
    }
    audio_uart_page_44131c(item->tile, 0, 0u);
    audio_uart_page_44146a(item->tile, 0, 0u);
    audio_uart_page_44127e(item->tile, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(item->tile, 0xffu, 0u);
    lv_obj_set_style_pad_all_54fa24(item->tile, 0, 0u);
    audio_uart_page_44120e(item->tile, 0x10, 0u);
    audio_uart_page_43dfa4(item->tile, LV_OBJ_FLAG_CLICKABLE_SCROLLABLE);

    item->card = audio_uart_page_43de82(item->tile);
    audio_uart_page_43f506(item->card, 0x224);
    audio_uart_page_43f568(item->card, LV_SIZE_CONTENT_FORK);
    audio_uart_page_4411aa(item->card, 0xc6, 0u);
    audio_uart_page_43f6b8(item->card, 9u, 0, 0);
    audio_uart_page_44131c(item->card, 1, 0u);
    audio_uart_page_4412ec(item->card, audio_uart_page_44104c(COLOR_WHITE), 0u);
    audio_uart_page_44146a(item->card, 6, 0u);
    audio_uart_page_44127e(item->card, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(item->card, 0xffu, 0u);
    lv_obj_set_style_pad_all_54fa24(item->card, 0x10, 0u);
    audio_uart_page_441238(item->card, 0xd, 0u);
    audio_uart_page_43dfa4(item->card, LV_OBJ_FLAG_CLICKABLE_SCROLLABLE);

    item->icon = audio_uart_page_498668(item->card);
    audio_uart_page_43f4c0(item->icon, 0x1e, 0x1e);
    audio_uart_page_498680(item->icon, g2_msg_notif_card_icon_769804);
    audio_uart_page_43f6b8(item->icon, 1u, 0, 0);

    if (msg_notif_create_content_obj_5514f0(item->card, &item->content) == NULL) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, fn_create_item, 0x6fdu, content_failed,
                               (uint32_t)index);
        if (compact_log_enabled())
            (void)compress_log_output(0x04400000u, content_failed_short, content_failed_short,
                                      (uint32_t)index);
        audio_lv_delete_44d7b8(item->tile);
        return NULL;
    }
    return item;
}

/* Fill tile `tile_index` with message `msg_index` (0 = newest) and re-flow
 * the title / subtitle row for whichever of the two is present. */
void msg_notif_fill_msg_item_551abc(g2_msg_notif_item_t *item, uint8_t msg_index,
                                    uint8_t tile_index)
{
    g2_msg_notif_content_t *content;
    g2_ancc_record_t *rec;
    uint8_t count;
    char time_text[32];

    if (item == NULL || item->tile == NULL)
        return;
    count = (uint8_t)audio_settings_unread_message_count();
    if (msg_index >= count) {
        audio_uart_page_43ded4(item->tile, LV_OBJ_FLAG_HIDDEN);
        return;
    }
    rec = service_ancc_record_find((uint8_t)(count - msg_index - 1u));
    if (rec == NULL || rec->used == 0u) {
        audio_uart_page_43ded4(item->tile, LV_OBJ_FLAG_HIDDEN);
        return;
    }
    msg_tile_binding_add_54ff64(item->tile, rec, msg_index, tile_index);

    {
        const char *app_identifier = rec->notif.app_identifier;
        const char *display_name = rec->notif.display_name;
        const char *date = rec->notif.date;
        const char *title = rec->notif.title;
        const char *subtitle = rec->notif.subtitle;
        const char *message = rec->notif.message;

        if (item->icon != NULL && app_identifier != NULL)
            navigation_apply_named_resource(item->icon, app_identifier);
        content = &item->content;
        if (content->obj != NULL) {
            const char *shown_title;
            const char *shown_app;
            const char *shown_subtitle;
            uint8_t has_title = 1u;
            uint8_t has_subtitle = 1u;

            if (content->app_name != NULL) {
                const char *name = text_empty;
                if (display_name != NULL)
                    name = display_name;
                else if (app_identifier != NULL)
                    name = navigation_record_third_field_lookup(app_identifier);
                audio_uart_page_49942e(content->app_name, name);
            }
            if (content->time != NULL && date != NULL) {
                msg_notif_format_time_54fb84(date, time_text, sizeof time_text);
                audio_uart_page_49942e(content->time, time_text);
            }
            if (content->title != NULL && title != NULL) {
                audio_uart_page_43f506(content->title, LV_SIZE_CONTENT_FORK);
                audio_uart_page_49942e(content->title, title);
            }
            if (content->subtitle != NULL && subtitle != NULL) {
                audio_uart_page_43f506(content->subtitle, LV_SIZE_CONTENT_FORK);
                audio_uart_page_49942e(content->subtitle, subtitle);
            }
            if (content->detail != NULL && message != NULL) {
                audio_uart_page_43f568(content->detail, LV_SIZE_CONTENT_FORK);
                audio_uart_page_layout_499678(content->detail, 0u);
                audio_uart_page_49942e(content->detail, message);
                audio_uart_page_43f66c(content->detail);
                if (audio_uart_lv_obj_height_43fdda(content->detail) > 90) {
                    audio_uart_page_43f568(content->detail, 90);
                    audio_uart_page_layout_499678(content->detail, 1u);
                }
            }

            /* A title equal to the app name is not repeated. */
            shown_title = audio_uart_page_text_pointer_4997f8(content->title);
            shown_app = audio_uart_page_text_pointer_4997f8(content->app_name);
            if (shown_title == NULL || *shown_title == '\0' ||
                (shown_app != NULL && audio_uart_font_path_compare(shown_title, shown_app) == 0)) {
                has_title = 0u;
                audio_uart_page_43ded4(content->title, LV_OBJ_FLAG_HIDDEN);
                audio_uart_page_43ded4(content->separator, LV_OBJ_FLAG_HIDDEN);
            } else {
                audio_uart_page_43dfa4(content->title, LV_OBJ_FLAG_HIDDEN);
            }
            shown_subtitle = audio_uart_page_text_pointer_4997f8(content->subtitle);
            if (shown_subtitle == NULL || *shown_subtitle == '\0') {
                has_subtitle = 0u;
                audio_uart_page_43ded4(content->subtitle, LV_OBJ_FLAG_HIDDEN);
                audio_uart_page_43ded4(content->separator, LV_OBJ_FLAG_HIDDEN);
            } else {
                audio_uart_page_43dfa4(content->subtitle, LV_OBJ_FLAG_HIDDEN);
            }

            if (has_title == 0u && has_subtitle == 0u) {
                audio_uart_page_43f6d6(content->detail, content->app_name, 13u, 0, 12);
            } else if (has_title == 0u) {
                audio_uart_page_43f506(content->subtitle, 0x1d9);
                audio_uart_page_43f6d6(content->subtitle, content->app_name, 13u, 0, 12);
                audio_uart_page_43f6d6(content->detail, content->subtitle, 13u, 0, 4);
            } else if (has_subtitle == 0u) {
                audio_uart_page_43f506(content->title, 0x1d9);
                audio_uart_page_43f6d6(content->title, content->app_name, 13u, 0, 12);
                audio_uart_page_43f6d6(content->detail, content->title, 13u, 0, 4);
            } else {
                int32_t title_width;
                int32_t subtitle_width;

                /* Both present: share 449 px, 224 px each when both are wide. */
                audio_uart_page_43dfa4(content->separator, LV_OBJ_FLAG_HIDDEN);
                audio_uart_page_43f506(content->title, LV_SIZE_CONTENT_FORK);
                audio_uart_page_43f506(content->subtitle, LV_SIZE_CONTENT_FORK);
                audio_uart_page_43f66c(content->title);
                audio_uart_page_43f66c(content->subtitle);
                title_width = audio_uart_lv_obj_width_43fd9e(content->title);
                subtitle_width = audio_uart_lv_obj_width_43fd9e(content->subtitle);
                if (title_width > 224 && subtitle_width > 224) {
                    audio_uart_page_43f506(content->title, 224);
                    audio_uart_page_43f506(content->subtitle, 224);
                } else if (title_width <= 224 && subtitle_width > 224) {
                    audio_uart_page_43f506(content->subtitle, 449 - title_width);
                } else if (title_width > 224 && subtitle_width <= 224) {
                    audio_uart_page_43f506(content->title, 449 - subtitle_width);
                }
                audio_uart_page_43f6d6(content->title, content->app_name, 13u, 0, 12);
                audio_uart_page_43f6d6(content->separator, content->title, 0x14u, 0, 0);
                audio_uart_page_43f6d6(content->subtitle, content->separator, 0x14u, 0, 0);
                audio_uart_page_43f6d6(content->detail, content->title, 13u, 0, 4);
            }
        }
    }

    audio_uart_page_43dfa4(item->tile, LV_OBJ_FLAG_HIDDEN);
    audio_uart_display_audio_reset_441488(item->tile, 0xffu, 0u);
    if (tile_index == 0u) {
        audio_uart_page_43f6b8(item->tile, 1u, 0, 0);
    } else {
        void *previous = g2_msg_notif_ui_2006f734.items[tile_index - 1u].tile;
        if (previous == NULL)
            audio_uart_page_43f6b8(item->tile, 1u, 0, 0);
        else
            audio_uart_page_43f6d6(item->tile, previous, 13u, 0, 0);
    }
}

/* Empty state versus list + indicator, then re-highlight the current dot. */
void msg_notif_refresh_visibility_551e5c(void)
{
    uint8_t count = (uint8_t)audio_settings_unread_message_count();

    if (count == 0u) {
        msg_notif_empty_show_55141c();
        msg_notif_tileview_hide_551464();
        msg_indicator_hide_5514bc();
    } else {
        msg_notif_empty_hide_551432();
        msg_notif_tileview_show_551448();
        msg_indicator_show_551494();
        msg_indicator_layout_550d3c(count);
        msg_indicator_update_550e2e(g2_msg_notif_current_index_20074cd0, 0u);
    }
}
