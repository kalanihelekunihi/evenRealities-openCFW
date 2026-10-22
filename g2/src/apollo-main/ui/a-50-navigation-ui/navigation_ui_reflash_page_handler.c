/* Navigation UI page message handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_ui.c
 * (log tag "navigation.ui", stock function navigation_ui_reflash_page_handler,
 * source lines 0x845..0xb5c). Native 0x549c24..0x54c245 including its
 * interleaved literal pools, trailing pool 0x54c248..0x54c267. Ghidra splits the "unknown navigation_ui_state"
 * tail (0x54c1f2) and the shared epilogue (0x54c240) into separate rows, both
 * are part of this function.
 *
 * Every page message is [cmd u8][input u8][value int32 LE]. The handler first
 * re-arms the heartbeat counter, answers heartbeats, then dispatches on the
 * page state at RAM 0x20074fed. Within a state the stock code is a chain of
 * independent `if (cmd == ...)` tests (not else-if) and that chain is kept:
 * in state 1 every command other than 0xf4 also reaches the final
 * "unknown cmd" log. */
#include <stdint.h>
#include <stddef.h>
#include "g2_ui_common_api.h"

/* ---- page messages ---- */
#define NAV_CMD_HEARTBEAT            0x00u
#define NAV_CMD_LOCATION_LIST        0x02u
#define NAV_CMD_NONE_LOCATION_LIST   0x03u
#define NAV_CMD_ERROR_INFO           0x06u
#define NAV_CMD_BASIC_INFO           0x07u
#define NAV_CMD_MINI_MAP_FILE        0x08u
#define NAV_CMD_MAX_MAP_FILE         0x09u
#define NAV_CMD_RECALCULATING        0x0au
#define NAV_CMD_COMPLETE             0x0bu
#define NAV_CMD_EXIT                 0x0cu
#define NAV_CMD_HEARTBEAT_TIMEOUT    0xf0u
#define NAV_CMD_INPUT                0xf2u
#define NAV_CMD_COMMON_TIMEOUT       0xf3u
#define NAV_CMD_SYSTEM_EXIT          0xf4u
#define NAV_CMD_FORCE_CALIBRATION    0xf5u
#define NAV_CMD_BMP_FORCE_SYNC       0xf6u
#define NAV_CMD_CALIBRATION_COMPLETE 0xf7u

/* input byte of NAV_CMD_INPUT */
#define NAV_INPUT_CLICK       0x0au
#define NAV_INPUT_COMPASS     0x41u
#define NAV_INPUT_SCROLL_UP   0x44u
#define NAV_INPUT_SCROLL_DOWN 0x45u
#define NAV_INPUT_DOUBLE_CLICK 0x48u

/* navigation_ui_state (RAM 0x20074fed) */
#define NAV_STATE_IDLE          0u
#define NAV_STATE_ROUTE_LOADING 1u
#define NAV_STATE_LOCATION_LIST 2u
#define NAV_STATE_EXIT_PAGE     4u
#define NAV_STATE_MAP           5u
#define NAV_STATE_7             7u  /* never entered from this handler */
#define NAV_STATE_BREAK_EXIT    8u
#define NAV_STATE_MODE_SELECT   9u
#define NAV_STATE_CALIBRATE     10u

#define NAV_APP_ID            8u        /* fade-out / system close / display reflash id */
#define NAV_EXIT_RECORD_KEY   0x40102u  /* usage record key, shared with EvenHub */
#define NAV_HEARTBEAT_RELOAD  20u
#define NAV_EXIT_COUNTDOWN    0xf0u
#define NAV_MODE_WALK         1u
#define NAV_MODE_BIKE         2u
#define LV_OBJ_FLAG_HIDDEN    1u
#define LV_SIZE_CONTENT       0x3fffffff
#define LV_ALIGN_CENTER       9u
#define LV_LABEL_LONG_WRAP    0u
#define LV_TEXT_ALIGN_CENTER  2u

/* Usage record {app, reason}: reason 1 system exit, 2 normal/error exit,
 * 3 heartbeat timeout. Stock keeps one 8-byte ROM initialiser per call site
 * (0x78dd64..0x78de13). */
typedef struct {
    uint32_t app;    /* +0x0 always 4 */
    uint32_t reason; /* +0x4 */
} g2_nav_exit_record_t;
_Static_assert(sizeof(g2_nav_exit_record_t) == 8u, "stock record is 8 bytes");

#define NAV_MAX_LOCATIONS 20
#define NAV_MINI_MAP_SIZE 18000u     /* 0x4650 */
#define NAV_MAX_MAP_SIZE 60000u      /* 0xea60 */

/* The three record types below are copied from ui/a-49-navigation-ui
 * (same TU, same RAM objects). */
typedef struct {
    uint32_t count;                               /* +0x000 */
    uint8_t header_04[2];                         /* +0x004 */
    char name[NAV_MAX_LOCATIONS][0x40];           /* +0x006 */
    uint8_t reserved_506[2];                      /* +0x506 */
    uint32_t icon_type[NAV_MAX_LOCATIONS];        /* +0x508 1 / 2 / other */
    uint8_t reserved_558[4];                      /* +0x558 (stock clears 0x55c bytes) */
} g2_navigation_location_list_t;
_Static_assert(sizeof(g2_navigation_location_list_t) == 0x55c, "location list");

typedef struct {
    uint8_t valid;                 /* +0x000 */
    uint8_t reserved_01[3];
    uint32_t field_04;             /* +0x004 */
    char distance[0x40];           /* +0x008 */
    char road_name[0x40];          /* +0x048 */
    char spend_time[0x40];         /* +0x088 */
    char remain_distance[0x40];    /* +0x0c8 */
    char eta_time[0x40];           /* +0x108 */
    char speed[0x40];              /* +0x148 */
    uint32_t navigate_work_method; /* +0x188 */
} g2_navigation_info_t;
_Static_assert(sizeof(g2_navigation_info_t) == 0x18c, "navigation info record");

typedef struct {
    g2_navigation_info_t info;                 /* +0x0000 */
    uint8_t mini_map_ready;                    /* +0x018c */
    uint8_t reserved_18d[3];
    uint32_t mini_map_size;                    /* +0x0190 */
    uint32_t mini_map_compress_mode;           /* +0x0194 */
    uint8_t reserved_198[4];
    uint8_t mini_map_data[NAV_MINI_MAP_SIZE];  /* +0x019c */
    uint8_t reserved_47ec;                     /* +0x47ec */
    uint8_t max_map_ready;                     /* +0x47ed */
    uint8_t reserved_47ee[2];
    uint32_t max_map_size;                     /* +0x47f0 */
    uint32_t max_map_compress_mode;            /* +0x47f4 */
    uint8_t max_map_data[NAV_MAX_MAP_SIZE];    /* +0x47f8 */
} g2_navigation_ui_data_t;
_Static_assert(offsetof(g2_navigation_ui_data_t, mini_map_ready) == 0x18c, "mini map flag");
_Static_assert(offsetof(g2_navigation_ui_data_t, max_map_ready) == 0x47ed, "max map flag");
_Static_assert(sizeof(g2_navigation_ui_data_t) == 0x13258, "navigation ui record");

/* generic_animation handle (ui/a-10-generic-animation); only the image is read. */
typedef struct {
    void *image; /* +0x00 lv_image */
} g2_generic_animation_t;

/* ---- logging ---- */
extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                           /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* ---- runtime / RTOS ---- */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t g2_log_module_length(const char *text);                      /* 0x44a43c strlen */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                  /* 0x44981c */

/* ---- LVGL ---- */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag); /* lv_obj_has_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);            /* lv_obj_is_valid */
extern void audio_uart_page_43f506(void *obj, int32_t w);                    /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                    /* lv_obj_set_height */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);               /* lv_obj_set_align */
extern void audio_uart_page_invalidate_440656(void *obj);                    /* lv_obj_invalidate */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel); /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* text_align */
extern void audio_uart_page_44d878(void *obj);                               /* lv_obj_clean */
extern void audio_uart_page_498680(void *image, const void *src);            /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                           /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);           /* lv_label_set_text */
extern void audio_uart_page_layout_499678(void *label, uint32_t mode);       /* lv_label_set_long_mode */

/* ---- product UI services ---- */
extern uint32_t audio_uart_page_460084(const char *key);                     /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);  /* localized text */
extern void generic_animation_destroy_463e1c(g2_generic_animation_t *anim, uint8_t delete_image);
extern void generic_animation_set_frame_463f5c(g2_generic_animation_t *anim, uint32_t frame);
extern uint32_t generic_animation_get_frame_463fa4(const g2_generic_animation_t *anim);
extern void Common_Fadeout_Anim_Start_4641b6(void *object, uint32_t app);
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);           /* 0x464bb2 */
extern void system_close_page_factory_0046ae9c(uint32_t style, int32_t app_id);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern uint32_t audio_uart_service_mode(void);                               /* 0x45a570, 1 = master */
extern uint32_t semantic_get_flag_20074fdc(void);                            /* compass calibrated */

/* ---- navigation_data_handler.c senders (TSV names) ---- */
extern void navigation_send_type_0_shared(uint8_t input);                    /* 0x586938 */
extern void navigation_send_type_1_shared(uint8_t input, uint32_t arg);      /* 0x587240 */
extern void navigation_send_type_4_allocating(uint32_t kind, const char *name, uint32_t name_len,
                                              uint32_t location_index, uint8_t mode); /* 0x586d64 */
extern void navigation_send_type_6_shared(uint8_t input, uint32_t arg);      /* 0x586a30 */
extern void navigation_send_type_7_shared(uint8_t input, uint32_t arg);      /* 0x586c20 */
extern void navigation_send_type_10_shared(uint8_t input, uint32_t arg);     /* 0x586aac */
extern void navigation_send_type_11_shared(uint8_t input, uint32_t arg);     /* 0x586b28 */
extern void navigation_send_type_12_shared(uint8_t input, uint32_t arg);     /* 0x586ba4 */
extern void navigation_send_type_14_allocating(uint32_t container_b);        /* 0x586f14 2 show, 1 hide */
extern void navigation_send_type_15_allocating(int32_t heading);             /* 0x58705c */
extern int32_t navigation_send_type_16_allocating(void);                     /* 0x5867fc */
extern void navigation_send_type_17_allocating(void);                        /* 0x5866c0 */

/* ---- navigation_ui.c rows defined in ui/a-48-navigation-ui and ui/a-49-navigation-ui ---- */
extern int32_t StartIMUCompassFunc_5455e4(void);
extern int32_t navigation_set_max_map_data_5458a2(void *img, const uint8_t *bmp);
extern void navigation_ui_update_map_texts_5464b8(void);
extern int32_t navigation_ui_create_calibrate_compass_page_546620(void);
extern int32_t navigation_ui_create_map_page_54692c(void);
extern void navigation_ui_create_break_exit_page_5476e4(void);
extern void navigation_ui_create_none_location_list_page_5477ac(void);
extern void navigation_ui_startup_failed_exit_page_54787c(uint32_t reason);
extern void navigation_ui_completed_exit_page_5479c8(void);
extern void navigation_show_container_B_thunk_54853a(void);
extern void navigation_hide_container_B_thunk_548542(void);
extern int32_t navigation_ui_create_location_list_page_5485c4(void);
extern int32_t navigation_ui_create_mode_list_page_548b98(void);
extern void navigation_ui_sync_navigation_info_5495a8(void);
extern void store_mini_map_data_549708(void);
extern void store_max_map_data_549994(void);
/* navigation_ui.c rows not yet reconstructed (stock names from their log records). */
extern void navigation_inject_event_54cfd0(uint8_t event);
extern void mode_inject_event_54e1a8(uint8_t event);
extern int32_t navigation_update_rotated_img_54e660(void *img, const uint8_t *bmp, int32_t w,
                                                    int32_t h, int32_t angle, uint32_t bpp);

/* ---- RAM state (names shared with a-48 / a-49 where they exist) ---- */
extern uint32_t g2_nav_var_20002cfc;                       /* RAM 0x20002cfc (.data) heartbeat counter */
extern char g2_nav_temp_buf_200705ec[0x100];               /* RAM 0x200705ec */
extern const void *audio_uart_ring_primary_head_cell;      /* RAM 0x200746dc: active lv_font_t * */
extern void *g2_navigation_page_root_20074718;             /* RAM 0x20074718 */
extern void *g2_navigation_mutex;                          /* RAM 0x2007471c */
extern uint32_t g2_nav_fadeout_pending_2007472c;           /* RAM 0x2007472c */
extern g2_ui_fifo_t *g2_nav_event_fifo_20074734;           /* RAM 0x20074734 map page events */
extern g2_ui_fifo_t *g2_nav_list_event_fifo_20074738;      /* RAM 0x20074738 list page events */
extern uint32_t g2_nav_container_b_shown_2007473c;         /* RAM 0x2007473c */
extern uint32_t g2_nav_var_20074748;                       /* RAM 0x20074748 exit countdown 0xf0 */
extern uint32_t g2_nav_var_2007474c;                       /* RAM 0x2007474c exit page active */
extern g2_generic_animation_t *g2_nav_calibrate_anim_20074750; /* RAM 0x20074750 */
extern uint32_t g2_nav_var_20074754;                       /* RAM 0x20074754 selected location index */
extern uint32_t g2_nav_var_20074758;                       /* RAM 0x20074758 */
extern void *g2_nav_max_map_img_2007477c;                  /* RAM 0x2007477c */
extern void *g2_nav_b_loading_label_20074780;              /* RAM 0x20074780 */
extern void *g2_nav_container_c_200747c8;                  /* RAM 0x200747c8 recalculating layer */
extern void *g2_nav_a_compass_img_200747e8;                /* RAM 0x200747e8 */
extern void *g2_nav_a_loading_label_200747ec;              /* RAM 0x200747ec */
extern uint32_t g2_nav_compass_enabled_20074808;           /* RAM 0x20074808 */
extern int32_t g2_nav_compass_heading_2007480c;            /* RAM 0x2007480c degrees */
extern int32_t g2_nav_compass_heading_last_20074810;       /* RAM 0x20074810 */
extern uint8_t g2_nav_flag_20074fe7;                       /* RAM 0x20074fe7 selected mode 1 walk / 2 bike */
extern uint8_t g2_navigation_location_animating_20074fe8;  /* RAM 0x20074fe8 */
extern uint8_t g2_navigation_mode_animating_20074fe9;      /* RAM 0x20074fe9 */
extern uint8_t g2_nav_animation_running_20074fec;          /* RAM 0x20074fec */
extern uint8_t g2_navigation_ui_state_20074fed;            /* RAM 0x20074fed */
extern uint8_t g2_nav_compass_shown_20074fee;              /* RAM 0x20074fee */
extern uint8_t g2_nav_buf_200f4784[0x40];                  /* RAM 0x200f4784 selected location name */
extern g2_navigation_ui_data_t g2_navigation_ui_data_202c0d70;         /* RAM 0x202c0d70 */
extern uint8_t g2_nav_buf_202e4fc8[0xea7c];                /* RAM 0x202e4fc8 */
extern uint8_t g2_navigation_max_map_decode_202f3a44[NAV_MAX_MAP_SIZE]; /* RAM 0x202f3a44 */
extern uint8_t g2_nav_buf_20329600[0x4674];                /* RAM 0x20329600 */
extern uint8_t g2_navigation_mini_map_decode_2032dc74[NAV_MINI_MAP_SIZE]; /* RAM 0x2032dc74 */
extern g2_navigation_location_list_t g2_navigation_location_list_20376c38; /* RAM 0x20376c38 (0x55c cleared) */
extern g2_navigation_info_t g2_navigation_info_staging_2037bdd0;       /* RAM 0x2037bdd0 */

static const char module_tag[] = "navigation.ui"; /* ROM 0x787ab0 */
static const char fmt_two_lines[] = "%s\n%s"; /* ROM 0x78dd5c */
static const char fn_reflash[] = "navigation_ui_reflash_page_handler"; /* ROM 0x756ef4 */
static const char id_loading_bike[] = "ID_NAVIGATE_LOADING_BIKE_ROUTE_TO"; /* ROM 0x756f3c */
static const char id_loading_walk[] = "ID_NAVIGATE_LOADING_WALK_ROUTE_TO"; /* ROM 0x756f18 */
static const char msg_anim_running_push[] = "animation running,push event to fifo"; /* ROM 0x74b98c */
static const char msg_anim_running_push_s[] = "[navigation.ui]animation running,push event to fifo"; /* ROM 0x72b1c8 */
static const char msg_basic_info[] = "navigation_ui_reflash_page_handler: receive basic info"; /* ROM 0x720788 */
static const char msg_basic_info_clear_label[] = "navigation_ui_reflash_page_handler: receive basic info,clear redirection label"; /* ROM 0x6ee9b8 */
static const char msg_basic_info_clear_label_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive basic info,clear redirection label"; /* ROM 0x6ddf54 */
static const char msg_basic_info_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive basic info"; /* ROM 0x6fb924 */
static const char msg_bmp_force_sync_cmd[] = "navigation_ui_reflash_page_handler: receive bmp force sync cmd"; /* ROM 0x70d124 */
static const char msg_bmp_force_sync_cmd_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive bmp force sync cmd"; /* ROM 0x6ee918 */
static const char msg_calibration_complete[] = "navigation_ui_reflash_page_handler: receive compass calibration complete"; /* ROM 0x6f4a2c */
static const char msg_calibration_complete_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive compass calibration complete"; /* ROM 0x6e4590 */
static const char msg_clicked_event[] = "navigation_ui_reflash_page_handler: receive clicked event"; /* ROM 0x71681c */
static const char msg_clicked_event_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive clicked event"; /* ROM 0x6f4948 */
static const char msg_cmd_input_value[] = "navigation_ui_reflash_page_handler: receive cmd: %d,input_value: %d"; /* ROM 0x7040a4 */
static const char msg_cmd_input_value_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive cmd: %d,input_value: %d"; /* ROM 0x6e8d7c */
static const char msg_common_timeout_exit[] = "navigation_ui_reflash_page_handler: receive common timeout exit"; /* ROM 0x70d1a4 */
static const char msg_common_timeout_exit_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive common timeout exit"; /* ROM 0x6eea58 */
static const char msg_compass_event[] = "navigation_ui_reflash_page_handler: receive compass event"; /* ROM 0x716984 */
static const char msg_compass_event_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive compass event"; /* ROM 0x6f4b10 */
static const char msg_create_map_page[] = "navigation_ui_reflash_page_handler: create map page,jump to map disp page"; /* ROM 0x6f4ba8 */
static const char msg_create_map_page_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: create map page,jump to map disp page"; /* ROM 0x6e0e14 */
static const char msg_error_info_msg[] = "navigation_ui_reflash_page_handler: receive error info msg"; /* ROM 0x716948 */
static const char msg_error_info_msg_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive error info msg"; /* ROM 0x6f4ac4 */
static const char msg_fifo_create_failed[] = "navigation_ui_startup_page_create: Failed to create event FIFO"; /* ROM 0x70cee4 */
static const char msg_fifo_create_failed_s[] = "[navigation.ui]navigation_ui_startup_page_create: Failed to create event FIFO"; /* ROM 0x6ee648 */
static const char msg_force_calib_ret[] = "navigation_data_handler send force update compass calibration to UI: ret = %d\n"; /* ROM 0x6ee8c8 */
static const char msg_force_calib_ret_s[] = "[navigation.ui]navigation_data_handler send force update compass calibration to UI: ret = %d\n"; /* ROM 0x6ddef4 */
static const char msg_force_calibration[] = "navigation_ui_reflash_page_handler: receive force update compass calibration"; /* ROM 0x6ee968 */
static const char msg_force_calibration_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive force update compass calibration"; /* ROM 0x6e0db8 */
static const char msg_heartbeat_cmd[] = "navigation_ui_reflash_page_handler: receive heartbeat cmd"; /* ROM 0x7167e0 */
static const char msg_heartbeat_cmd_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive heartbeat cmd"; /* ROM 0x6f48fc */
static const char msg_heartbeat_timeout[] = "navigation_ui_reflash_page_handler: receive heartbeat timeout"; /* ROM 0x70d024 */
static const char msg_heartbeat_timeout_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive heartbeat timeout"; /* ROM 0x6ee7d8 */
static const char msg_hide_container_b[] = "navigation_ui_reflash_page_handler: hide container B"; /* ROM 0x7205c8 */
static const char msg_hide_container_b_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: hide container B"; /* ROM 0x703f94 */
static const char msg_input_event[] = "navigation_ui_reflash_page_handler: receive input event"; /* ROM 0x720750 */
static const char msg_input_event_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive input event"; /* ROM 0x6fb894 */
static const char msg_length_is_0[] = "navigation_ui_reflash_page_handler: length is 0"; /* ROM 0x735ad4 */
static const char msg_length_is_0_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: length is 0"; /* ROM 0x70cfa4 */
static const char msg_location_select[] = "navigation_notify_location_select_index_cmd: navigation_select_location_name=%s, navigation_select_location_index=%d, navigation_select_mode_index=%d"; /* ROM 0x6d38e8 */
static const char msg_location_select_s[] = "[navigation.ui]navigation_notify_location_select_index_cmd: navigation_select_location_name=%s, navigation_select_location_index=%d, navigation_select_mode_index=%d"; /* ROM 0x6d2a78 */
static const char msg_max_map_file[] = "navigation_ui_reflash_page_handler: receive max map file"; /* ROM 0x71690c */
static const char msg_max_map_file_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive max map file"; /* ROM 0x6fb8dc */
static const char msg_mini_map_file[] = "navigation_ui_reflash_page_handler: receive mini map file"; /* ROM 0x7168d0 */
static const char msg_mini_map_file_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive mini map file"; /* ROM 0x6f4a78 */
static const char msg_mode_select_clicked_event[] = "NAVIGATION_MODE_SELECT_PAGE: receive clicked event"; /* ROM 0x72b230 */
static const char msg_mode_select_clicked_event_s[] = "[navigation.ui]NAVIGATION_MODE_SELECT_PAGE: receive clicked event"; /* ROM 0x7040e8 */
static const char msg_mode_select_input_event[] = "NAVIGATION_MODE_SELECT_PAGE: receive input event"; /* ROM 0x72b1fc */
static const char msg_mode_select_input_event_s[] = "[navigation.ui]NAVIGATION_MODE_SELECT_PAGE: receive input event"; /* ROM 0x70d0e4 */
static const char msg_navigation_complete[] = "navigation_ui_reflash_page_handler: receive navigation complete cmd"; /* ROM 0x70412c */
static const char msg_navigation_complete_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive navigation complete cmd"; /* ROM 0x6e8dd0 */
static const char msg_none_location_list[] = "navigation_ui_reflash_page_handler: receive none location list"; /* ROM 0x70cfe4 */
static const char msg_none_location_list_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive none location list"; /* ROM 0x6ee788 */
static const char msg_recalculating[] = "navigation_ui_reflash_page_handler: receive recalculating location start cmd"; /* ROM 0x6eea08 */
static const char msg_recalculating_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive recalculating location start cmd"; /* ROM 0x6e0e70 */
static const char msg_scroll_down_event[] = "navigation_ui_reflash_page_handler: receive scroll down event"; /* ROM 0x70d0a4 */
static const char msg_scroll_down_event_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive scroll down event"; /* ROM 0x6ee878 */
static const char msg_scroll_up_event[] = "navigation_ui_reflash_page_handler: receive scroll up event"; /* ROM 0x716858 */
static const char msg_scroll_up_event_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive scroll up event"; /* ROM 0x6f4994 */
static const char msg_show_container_b[] = "navigation_ui_reflash_page_handler: show container B"; /* ROM 0x720590 */
static const char msg_show_container_b_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: show container B"; /* ROM 0x703f50 */
static const char msg_system_exit_notify[] = "navigation_ui_reflash_page_handler: receive system exit notify"; /* ROM 0x70d064 */
static const char msg_system_exit_notify_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive system exit notify"; /* ROM 0x6ee828 */
static const char msg_temp_buf_loading_string[] = "temp_buf_loading_string: %s"; /* ROM 0x76e788 */
static const char msg_temp_buf_loading_string_s[] = "[navigation.ui]temp_buf_loading_string: %s"; /* ROM 0x740600 */
static const char msg_ui_state[] = "navigation_ui_state: %d"; /* ROM 0x779994 */
static const char msg_ui_state_s[] = "[navigation.ui]navigation_ui_state: %d"; /* ROM 0x74b964 */
static const char msg_unknown_cmd[] = "navigation_ui_reflash_page_handler: receive unknown cmd: %d"; /* ROM 0x716894 */
static const char msg_unknown_cmd_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: receive unknown cmd: %d"; /* ROM 0x6f49e0 */
static const char msg_unknown_state[] = "unknown navigation_ui_state: %d"; /* ROM 0x7626f0 */
static const char msg_unknown_state_s[] = "[navigation.ui]unknown navigation_ui_state: %d"; /* ROM 0x735b04 */
static const char msg_update_compass_value[] = "navigation_ui_reflash_page_handler: update compass value: %d"; /* ROM 0x70d164 */
static const char msg_update_compass_value_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: update compass value: %d"; /* ROM 0x6f4b5c */
static const char msg_update_rotated_img[] = "navigation_ui_reflash_page_handler: update rotated img"; /* ROM 0x7207c0 */
static const char msg_update_rotated_img_s[] = "[navigation.ui]navigation_ui_reflash_page_handler: update rotated img"; /* ROM 0x6fb96c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_ui.c"; /* ROM 0x6fb6e4 */

/* Stock log macro expansion: full record when flag bit 1 is set, compressed
 * record (the "[navigation.ui]" twin, `name##_s`) when bit 0 or bit 2 is set. */
#define NAV_LOG(level, line, cflags, name, ...)                                                   \
    do {                                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                                       \
            audio_log_extended((level), module_tag, source_file, fn_reflash, (line), name,        \
                               ##__VA_ARGS__);                                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                     \
            (void)compress_log_output((cflags), name##_s, name##_s, ##__VA_ARGS__);              \
    } while (0)

static void nav_write_exit_record(uint32_t reason)
{
    const g2_nav_exit_record_t record = {4u, reason};
    audio_uart_ring_wear_persist_48eb32(NAV_EXIT_RECORD_KEY, 2u, &record);
}

/* NAV_CMD_EXIT (0x0c), common to every state that handles it. */
static void nav_exit_fadeout(uint8_t input)
{
    navigation_send_type_12_shared(input, 0u);
    Common_Fadeout_Anim_Start_4641b6(g2_navigation_page_root_20074718, NAV_APP_ID);
}

/* Switch to the "break" exit page (heartbeat timeout, 0xf0). */
static void nav_heartbeat_timeout(uint32_t line, int create_first)
{
    NAV_LOG(4u, line, 0x10000000u, msg_heartbeat_timeout);
    audio_uart_page_44d878(g2_navigation_page_root_20074718);
    g2_navigation_ui_state_20074fed = NAV_STATE_BREAK_EXIT;
    if (create_first) {
        navigation_ui_create_break_exit_page_5476e4();
        g2_nav_var_2007474c = 1u;
        nav_write_exit_record(3u);
    } else {
        nav_write_exit_record(3u);
        navigation_ui_create_break_exit_page_5476e4();
        g2_nav_var_2007474c = 1u;
    }
    g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
}

/* NAV_CMD_SYSTEM_EXIT (0xf4) outside the exit pages. */
static void nav_system_exit(uint32_t line)
{
    NAV_LOG(4u, line, 0x10000000u, msg_system_exit_notify);
    Common_Fadeout_Anim_Start_4641b6(g2_navigation_page_root_20074718, NAV_APP_ID);
    g2_nav_fadeout_pending_2007472c = 1u;
    nav_write_exit_record(1u);
}

/* States 4, 7 and 8 (exit pages): only exit, common timeout and system exit. */
static void nav_exit_page_state(uint8_t cmd, uint8_t input, uint32_t timeout_line,
                                uint32_t exit_line)
{
    if (cmd == NAV_CMD_EXIT) {
        nav_exit_fadeout(input);
        g2_nav_fadeout_pending_2007472c = 1u;
    }
    if (cmd == NAV_CMD_COMMON_TIMEOUT) {
        NAV_LOG(4u, timeout_line, 0x10000000u, msg_common_timeout_exit);
        Common_Fadeout_Anim_Start_4641b6(g2_navigation_page_root_20074718, NAV_APP_ID);
        g2_nav_fadeout_pending_2007472c = 1u;
    }
    if (cmd == NAV_CMD_SYSTEM_EXIT) {
        NAV_LOG(4u, exit_line, 0x10000000u, msg_system_exit_notify);
        Common_Fadeout_Anim_Start_4641b6(g2_navigation_page_root_20074718, NAV_APP_ID);
        g2_nav_fadeout_pending_2007472c = 1u;
    }
}

int32_t navigation_ui_reflash_page_handler_549c24(const uint8_t *data, uint16_t length);

/* Returns -1 for an empty message. The stock function has no other return
 * value (r0 is whatever the last call left); 0 is returned here. */
int32_t navigation_ui_reflash_page_handler_549c24(const uint8_t *data, uint16_t length)
{
    if (length == 0u) {
        NAV_LOG(1u, 0x845u, 0x04000000u, msg_length_is_0);
        return -1;
    }

    const uint8_t cmd = data[0];
    uint8_t input = data[1]; /* address taken: queued in the list FIFO */
    const int32_t value = (int32_t)((uint32_t)data[2] | ((uint32_t)data[3] << 8) |
                                    ((uint32_t)data[4] << 16) | ((uint32_t)data[5] << 24));

    NAV_LOG(4u, 0x84eu, 0x10800000u, msg_cmd_input_value, (uint32_t)cmd, value);

    if (cmd == NAV_CMD_HEARTBEAT || length != 0u) {
        g2_nav_var_20002cfc = NAV_HEARTBEAT_RELOAD;
        if (cmd == NAV_CMD_HEARTBEAT) {
            navigation_send_type_0_shared(input);
            NAV_LOG(4u, 0x854u, 0x10000000u, msg_heartbeat_cmd);
        }
    }

    NAV_LOG(4u, 0x858u, 0x10400000u, msg_ui_state, (uint32_t)g2_navigation_ui_state_20074fed);

    switch (g2_navigation_ui_state_20074fed) {
    case NAV_STATE_IDLE:
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x85eu, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_LOCATION_LIST) {
            navigation_send_type_1_shared(input, 0u);
            (void)navigation_ui_create_location_list_page_5485c4(); /* stock r0 = page root */
            g2_navigation_ui_state_20074fed = NAV_STATE_LOCATION_LIST;
            g2_navigation_location_animating_20074fe8 = 0u;
            g2_navigation_mode_animating_20074fe9 = 0u;
            if (g2_nav_list_event_fifo_20074738 != NULL) {
                ui_common_api_fn_00509c96(g2_nav_list_event_fifo_20074738);
                g2_nav_list_event_fifo_20074738 = NULL;
            }
            if (g2_nav_list_event_fifo_20074738 == NULL) {
                g2_nav_list_event_fifo_20074738 = ui_common_api_fn_00509c1c();
                if (g2_nav_list_event_fifo_20074738 == NULL) {
                    NAV_LOG(1u, 0x874u, 0x04000000u, msg_fifo_create_failed);
                    return 0;
                }
            }
        } else if (cmd == NAV_CMD_NONE_LOCATION_LIST) {
            NAV_LOG(3u, 0x879u, 0x0c000000u, msg_none_location_list);
            g2_navigation_ui_state_20074fed = NAV_STATE_BREAK_EXIT;
            nav_write_exit_record(2u);
            navigation_ui_create_none_location_list_page_5477ac();
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
        } else if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT) {
            nav_heartbeat_timeout(0x880u, 0);
        } else if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            nav_write_exit_record(2u);
            g2_nav_fadeout_pending_2007472c = 1u;
        } else if (cmd == NAV_CMD_SYSTEM_EXIT) {
            nav_system_exit(0x88eu);
        }
        break;

    case NAV_STATE_LOCATION_LIST:
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x89au, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x8a3u, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_CLICK) {
                NAV_LOG(4u, 0x8a5u, 0x10000000u, msg_clicked_event);
                if (g2_navigation_location_animating_20074fe8 == 1u) {
                    NAV_LOG(4u, 0x8a7u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    navigation_inject_event_54cfd0(2u);
                    if (g2_navigation_page_root_20074718 != NULL)
                        audio_uart_page_44d878(g2_navigation_page_root_20074718);
                    g2_navigation_ui_state_20074fed = NAV_STATE_MODE_SELECT;
                    g2_navigation_mode_animating_20074fe9 = 0u;
                    g2_navigation_location_animating_20074fe8 = 0u;
                    ui_common_api_fn_00509f52(g2_nav_list_event_fifo_20074738);
                    (void)navigation_ui_create_mode_list_page_548b98();
                }
            } else if (input == NAV_INPUT_SCROLL_UP) {
                NAV_LOG(4u, 0x8b7u, 0x10000000u, msg_scroll_up_event);
                if (g2_navigation_location_animating_20074fe8 == 1u) {
                    NAV_LOG(4u, 0x8b9u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    navigation_inject_event_54cfd0(1u);
                }
            } else if (input == NAV_INPUT_SCROLL_DOWN) {
                NAV_LOG(4u, 0x8bfu, 0x10000000u, msg_scroll_down_event);
                if (g2_navigation_location_animating_20074fe8 == 1u) {
                    NAV_LOG(4u, 0x8c1u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    navigation_inject_event_54cfd0(0u);
                }
            }
        } else if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT) {
            nav_heartbeat_timeout(0x8c8u, 0);
        } else if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            nav_write_exit_record(2u);
            g2_nav_fadeout_pending_2007472c = 1u;
        } else if (cmd == NAV_CMD_SYSTEM_EXIT) {
            nav_system_exit(0x8d6u);
        } else {
            NAV_LOG(2u, 0x8dbu, 0x08400000u, msg_unknown_cmd, (uint32_t)cmd);
        }
        break;

    case NAV_STATE_MODE_SELECT:
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x8e5u, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x8efu, 0x10000000u, msg_mode_select_input_event);
            if (input == NAV_INPUT_CLICK) {
                NAV_LOG(4u, 0x8f1u, 0x10000000u, msg_mode_select_clicked_event);
                if (g2_navigation_mode_animating_20074fe9 == 1u) {
                    NAV_LOG(4u, 0x8f3u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    const char *name = (const char *)g2_nav_buf_200f4784;
                    mode_inject_event_54e1a8(2u);
                    NAV_LOG(3u, 0x8f7u, 0x0cc00000u, msg_location_select, name,
                            g2_nav_var_20074754, (uint32_t)g2_nav_flag_20074fe7);
                    if (g2_navigation_page_root_20074718 != NULL)
                        audio_uart_page_44d878(g2_navigation_page_root_20074718);
                    /* Centered "loading route to\n<name>" label on the page root. */
                    void *label = audio_uart_page_499416(g2_navigation_page_root_20074718);
                    audio_uart_page_43f506(label, 0x23a);
                    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
                    audio_uart_page_43f6ac(label, LV_ALIGN_CENTER);
                    audio_uart_page_layout_499678(label, LV_LABEL_LONG_WRAP);
                    if (g2_nav_flag_20074fe7 == NAV_MODE_WALK) {
                        const char *text =
                            audio_uart_page_45fffe(id_loading_walk, audio_uart_page_460084(id_loading_walk));
                        (void)g2_audio_dump_snprintf(g2_nav_temp_buf_200705ec, 0x100u, fmt_two_lines,
                                                     text, name);
                        NAV_LOG(4u, 0x905u, 0x10400000u, msg_temp_buf_loading_string,
                                g2_nav_temp_buf_200705ec);
                        audio_uart_page_49942e(label, g2_nav_temp_buf_200705ec);
                    } else if (g2_nav_flag_20074fe7 == NAV_MODE_BIKE) {
                        const char *text =
                            audio_uart_page_45fffe(id_loading_bike, audio_uart_page_460084(id_loading_bike));
                        (void)g2_audio_dump_snprintf(g2_nav_temp_buf_200705ec, 0x100u, fmt_two_lines,
                                                     text, name);
                        NAV_LOG(4u, 0x90au, 0x10400000u, msg_temp_buf_loading_string,
                                g2_nav_temp_buf_200705ec);
                        audio_uart_page_49942e(label, g2_nav_temp_buf_200705ec);
                    }
                    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
                    audio_uart_page_44145a(label, LV_TEXT_ALIGN_CENTER, 0u);
                    audio_uart_page_invalidate_440656(g2_navigation_page_root_20074718);
                    g2_navigation_ui_state_20074fed = NAV_STATE_ROUTE_LOADING;
                    navigation_send_type_4_allocating(0u, name, g2_log_module_length(name),
                                                      g2_nav_var_20074754, g2_nav_flag_20074fe7);
                    (void)StartIMUCompassFunc_5455e4();
                    /* Master side without a calibrated compass: ask the phone and
                     * inject a "force update compass calibration" message (cmd
                     * 0xf5) into this page through the display reflash path. */
                    if (audio_uart_service_mode() == 1u && semantic_get_flag_20074fdc() == 0u) {
                        uint8_t msg[10];
                        (void)navigation_send_type_16_allocating();
                        (void)aeabi_memset_43c0e4(msg, sizeof msg, 0);
                        msg[0] = NAV_CMD_FORCE_CALIBRATION;
                        msg[1] = 0u;
                        msg[2] = 0u;
                        msg[3] = 0u;
                        msg[4] = 0u;
                        msg[5] = 0u;
                        uint32_t ret = audio_uart_master_display_refresh(NAV_APP_ID, msg, 6u, 0u);
                        NAV_LOG(4u, 0x924u, 0x10400000u, msg_force_calib_ret, ret);
                    }
                }
            } else if (input == NAV_INPUT_SCROLL_UP) {
                NAV_LOG(4u, 0x92bu, 0x10000000u, msg_scroll_up_event);
                if (g2_navigation_mode_animating_20074fe9 == 1u) {
                    NAV_LOG(4u, 0x92du, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    mode_inject_event_54e1a8(1u);
                }
            } else if (input == NAV_INPUT_SCROLL_DOWN) {
                NAV_LOG(4u, 0x933u, 0x10000000u, msg_scroll_down_event);
                if (g2_navigation_mode_animating_20074fe9 == 1u) {
                    NAV_LOG(4u, 0x935u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_list_event_fifo_20074738, &input, 1u);
                } else {
                    mode_inject_event_54e1a8(0u);
                }
            }
        } else if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT) {
            nav_heartbeat_timeout(0x93cu, 0);
        } else if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            g2_nav_fadeout_pending_2007472c = 1u;
            nav_write_exit_record(2u);
        } else if (cmd == NAV_CMD_SYSTEM_EXIT) {
            nav_system_exit(0x94fu);
        } else {
            NAV_LOG(2u, 0x954u, 0x08400000u, msg_unknown_cmd, (uint32_t)cmd);
        }
        break;

    case NAV_STATE_CALIBRATE:
        if (cmd == NAV_CMD_BMP_FORCE_SYNC) {
            NAV_LOG(4u, 0x95fu, 0x10000000u, msg_bmp_force_sync_cmd);
            g2_generic_animation_t *anim = g2_nav_calibrate_anim_20074750;
            if (anim != NULL && audio_terminal_ui_object_valid_43e2ea(anim->image) != 0u &&
                generic_animation_get_frame_463fa4(anim) != data[1])
                generic_animation_set_frame_463f5c(anim, data[1]);
        }
        if (cmd == NAV_CMD_CALIBRATION_COMPLETE) {
            NAV_LOG(4u, 0x968u, 0x10000000u, msg_calibration_complete);
            g2_navigation_ui_state_20074fed = NAV_STATE_ROUTE_LOADING;
            navigation_send_type_17_allocating();
            break;
        }
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x96fu, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_MINI_MAP_FILE) {
            NAV_LOG(4u, 0x982u, 0x10000000u, msg_mini_map_file);
            store_mini_map_data_549708();
            g2_nav_compass_shown_20074fee = 1u;
        }
        if (cmd == NAV_CMD_MAX_MAP_FILE) {
            NAV_LOG(4u, 0x98au, 0x10000000u, msg_max_map_file);
            store_max_map_data_549994();
        }
        if (cmd == NAV_CMD_ERROR_INFO) {
            NAV_LOG(4u, 0x98fu, 0x10000000u, msg_error_info_msg);
            g2_navigation_ui_state_20074fed = NAV_STATE_EXIT_PAGE;
            nav_write_exit_record(2u);
            generic_animation_destroy_463e1c(g2_nav_calibrate_anim_20074750, 1u);
            g2_nav_calibrate_anim_20074750 = NULL;
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
            navigation_send_type_6_shared(input, 0u);
            if (g2_navigation_page_root_20074718 != NULL)
                audio_uart_page_44d878(g2_navigation_page_root_20074718);
            navigation_ui_startup_failed_exit_page_54787c((uint32_t)value);
        }
        if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            g2_nav_fadeout_pending_2007472c = 1u;
            nav_write_exit_record(2u);
        }
        if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT) {
            NAV_LOG(4u, 0x9a5u, 0x10000000u, msg_heartbeat_timeout);
            audio_uart_page_44d878(g2_navigation_page_root_20074718);
            g2_navigation_ui_state_20074fed = NAV_STATE_BREAK_EXIT;
            nav_write_exit_record(3u);
            generic_animation_destroy_463e1c(g2_nav_calibrate_anim_20074750, 1u);
            g2_nav_calibrate_anim_20074750 = NULL;
            navigation_ui_create_break_exit_page_5476e4();
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
        }
        if (cmd == NAV_CMD_SYSTEM_EXIT)
            nav_system_exit(0x9b1u);
        break;

    case NAV_STATE_ROUTE_LOADING:
        if (cmd == NAV_CMD_FORCE_CALIBRATION) {
            NAV_LOG(3u, 0x9bdu, 0x0c000000u, msg_force_calibration);
            g2_navigation_ui_state_20074fed = NAV_STATE_CALIBRATE;
            (void)navigation_ui_create_calibrate_compass_page_546620();
            return 0;
        }
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0x9c4u, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_COMPASS) {
                NAV_LOG(4u, 0x9c7u, 0x10000000u, msg_compass_event);
                if (g2_nav_compass_enabled_20074808 != 1u)
                    return 0;
                g2_nav_compass_heading_2007480c = value;
                navigation_send_type_15_allocating(g2_nav_compass_heading_2007480c);
                NAV_LOG(4u, 0x9cbu, 0x10400000u, msg_update_compass_value,
                        g2_nav_compass_heading_2007480c);
                return 0;
            }
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_BASIC_INFO) {
            NAV_LOG(4u, 0x9d9u, 0x10000000u, msg_basic_info);
            navigation_ui_sync_navigation_info_5495a8();
            g2_generic_animation_t *anim = g2_nav_calibrate_anim_20074750;
            if (anim != NULL && audio_terminal_ui_object_valid_43e2ea(anim->image) != 0u) {
                generic_animation_destroy_463e1c(anim, 1u);
                g2_nav_calibrate_anim_20074750 = NULL;
            }
            navigation_send_type_7_shared(input, 0u);
            (void)navigation_ui_create_map_page_54692c();
            g2_navigation_ui_state_20074fed = NAV_STATE_MAP;
            g2_nav_container_b_shown_2007473c = 0u;
            g2_nav_compass_heading_last_20074810 = 0;
            NAV_LOG(4u, 0x9e7u, 0x10000000u, msg_create_map_page);
        }
        if (cmd == NAV_CMD_MINI_MAP_FILE) {
            NAV_LOG(4u, 0x9ebu, 0x10000000u, msg_mini_map_file);
            store_mini_map_data_549708();
            if (g2_navigation_ui_data_202c0d70.mini_map_ready == 1u) {
                if (g2_nav_a_loading_label_200747ec != NULL &&
                    audio_terminal_ui_object_valid_43e2ea(g2_nav_a_loading_label_200747ec) != 0u)
                    audio_uart_page_43ded4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
                g2_nav_compass_shown_20074fee = 1u;
            }
        }
        if (cmd == NAV_CMD_MAX_MAP_FILE) {
            NAV_LOG(4u, 0x9f7u, 0x10000000u, msg_max_map_file);
            store_max_map_data_549994();
            if (g2_navigation_ui_data_202c0d70.max_map_ready == 1u) {
                if (g2_nav_b_loading_label_20074780 != NULL &&
                    audio_terminal_ui_object_valid_43e2ea(g2_nav_b_loading_label_20074780) != 0u)
                    audio_uart_page_43ded4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_HIDDEN);
                if (g2_nav_max_map_img_2007477c != NULL &&
                    audio_terminal_ui_object_valid_43e2ea(g2_nav_max_map_img_2007477c) != 0u)
                    (void)navigation_set_max_map_data_5458a2(g2_nav_max_map_img_2007477c,
                                                             g2_navigation_max_map_decode_202f3a44);
            }
        }
        if (cmd == NAV_CMD_ERROR_INFO) {
            NAV_LOG(4u, 0xa04u, 0x10000000u, msg_error_info_msg);
            g2_navigation_ui_state_20074fed = NAV_STATE_EXIT_PAGE;
            nav_write_exit_record(2u);
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
            navigation_send_type_6_shared(input, 0u);
            if (g2_navigation_page_root_20074718 != NULL)
                audio_uart_page_44d878(g2_navigation_page_root_20074718);
            navigation_ui_startup_failed_exit_page_54787c((uint32_t)value);
        }
        if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            g2_nav_fadeout_pending_2007472c = 1u;
            nav_write_exit_record(2u);
        }
        if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT)
            nav_heartbeat_timeout(0xa1eu, 1);
        if (cmd == NAV_CMD_SYSTEM_EXIT)
            nav_system_exit(0xa28u);
        else
            NAV_LOG(2u, 0xa2du, 0x08400000u, msg_unknown_cmd, (uint32_t)cmd);
        break;

    case NAV_STATE_MAP:
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0xa36u, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_DOUBLE_CLICK) {
                system_close_page_factory_0046ae9c(1u, NAV_APP_ID);
                return 0;
            }
        }
        if (cmd == NAV_CMD_BASIC_INFO) {
            NAV_LOG(4u, 0xa40u, 0x10000000u, msg_basic_info);
            if ((uint8_t)audio_uart_lv_obj_has_flag_43e0e0(g2_nav_container_c_200747c8,
                                                           LV_OBJ_FLAG_HIDDEN) == 0u) {
                NAV_LOG(3u, 0xa43u, 0x0c000000u, msg_basic_info_clear_label);
                audio_uart_page_43ded4(g2_nav_container_c_200747c8, LV_OBJ_FLAG_HIDDEN);
            }
            navigation_ui_sync_navigation_info_5495a8();
            navigation_send_type_7_shared(input, 0u);
            navigation_ui_update_map_texts_5464b8();
        }
        if (cmd == NAV_CMD_MINI_MAP_FILE) {
            NAV_LOG(4u, 0xa4cu, 0x10000000u, msg_mini_map_file);
            store_mini_map_data_549708();
            if (g2_navigation_ui_data_202c0d70.mini_map_ready == 1u) {
                /* LVGL rotation is in 0.1 degree: 3600 - heading * 10. */
                (void)navigation_update_rotated_img_54e660(g2_nav_a_compass_img_200747e8,
                                                           g2_navigation_mini_map_decode_2032dc74,
                                                           0xaa, 0xaa,
                                                           g2_nav_compass_heading_2007480c * -10 + 0xe10,
                                                           4u);
                g2_nav_compass_shown_20074fee = 1u;
                audio_uart_page_43ded4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
            } else {
                audio_uart_page_43dfa4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
            }
        }
        if (cmd == NAV_CMD_MAX_MAP_FILE) {
            NAV_LOG(4u, 0xa6au, 0x10000000u, msg_max_map_file);
            store_max_map_data_549994();
            if (g2_navigation_ui_data_202c0d70.max_map_ready == 1u) {
                (void)navigation_set_max_map_data_5458a2(g2_nav_max_map_img_2007477c,
                                                         g2_navigation_max_map_decode_202f3a44);
                audio_uart_page_43ded4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_HIDDEN);
            }
        }
        if (cmd == NAV_CMD_INPUT) {
            NAV_LOG(4u, 0xa74u, 0x10000000u, msg_input_event);
            if (input == NAV_INPUT_CLICK) {
                NAV_LOG(4u, 0xa76u, 0x10000000u, msg_clicked_event);
                if (g2_nav_animation_running_20074fec == 1u) {
                    NAV_LOG(4u, 0xa78u, 0x10000000u, msg_anim_running_push);
                    (void)ui_common_api_fn_00509ca2(g2_nav_event_fifo_20074734, data + 1, 5u);
                } else if (g2_nav_container_b_shown_2007473c == 0u) {
                    g2_nav_container_b_shown_2007473c = 1u;
                    NAV_LOG(4u, 0xa7du, 0x10000000u, msg_show_container_b);
                    navigation_show_container_B_thunk_54853a();
                    navigation_send_type_14_allocating(2u);
                } else {
                    g2_nav_container_b_shown_2007473c = 0u;
                    NAV_LOG(4u, 0xa82u, 0x10000000u, msg_hide_container_b);
                    navigation_hide_container_B_thunk_548542();
                    navigation_send_type_14_allocating(1u);
                }
            } else if (input == NAV_INPUT_COMPASS) {
                NAV_LOG(4u, 0xa88u, 0x10000000u, msg_compass_event);
                if (g2_nav_compass_enabled_20074808 == 1u) {
                    g2_nav_compass_heading_2007480c = value;
                    navigation_send_type_15_allocating(g2_nav_compass_heading_2007480c);
                    NAV_LOG(4u, 0xa8du, 0x10400000u, msg_update_compass_value,
                            g2_nav_compass_heading_2007480c);
                }
                if (g2_navigation_ui_data_202c0d70.mini_map_ready == 1u &&
                    g2_nav_compass_shown_20074fee == 1u && g2_nav_compass_enabled_20074808 == 1u) {
                    NAV_LOG(4u, 0xa91u, 0x10000000u, msg_update_rotated_img);
                    (void)navigation_update_rotated_img_54e660(g2_nav_a_compass_img_200747e8,
                                                               g2_navigation_mini_map_decode_2032dc74,
                                                               0xaa, 0xaa,
                                                               g2_nav_compass_heading_2007480c * -10 + 0xe10,
                                                               4u);
                    audio_uart_page_43ded4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
                }
                g2_nav_compass_heading_last_20074810 = value;
                NAV_LOG(3u, 0xaa7u, 0x0c400000u, msg_update_compass_value,
                        g2_nav_compass_heading_last_20074810);
            }
        }
        if (cmd == NAV_CMD_EXIT) {
            nav_exit_fadeout(input);
            g2_nav_fadeout_pending_2007472c = 1u;
            nav_write_exit_record(2u);
        }
        if (cmd == NAV_CMD_HEARTBEAT_TIMEOUT)
            nav_heartbeat_timeout(0xabau, 1);
        if (cmd == NAV_CMD_COMPLETE) {
            NAV_LOG(4u, 0xac5u, 0x10000000u, msg_navigation_complete);
            g2_navigation_ui_state_20074fed = NAV_STATE_EXIT_PAGE;
            g2_nav_var_2007474c = 1u;
            g2_nav_var_20074748 = NAV_EXIT_COUNTDOWN;
            navigation_send_type_11_shared(input, 0u);
            audio_uart_page_44d878(g2_navigation_page_root_20074718);
            navigation_ui_completed_exit_page_5479c8();
            nav_write_exit_record(2u);
        }
        if (cmd == NAV_CMD_RECALCULATING) {
            NAV_LOG(4u, 0xad1u, 0x10000000u, msg_recalculating);
            navigation_send_type_10_shared(input, 0u);
            audio_uart_page_43dfa4(g2_nav_container_c_200747c8, LV_OBJ_FLAG_HIDDEN);
            g2_nav_compass_shown_20074fee = 0u;
            audio_uart_page_43dfa4(g2_nav_a_loading_label_200747ec, LV_OBJ_FLAG_HIDDEN);
            audio_uart_page_43dfa4(g2_nav_b_loading_label_20074780, LV_OBJ_FLAG_HIDDEN);
            audio_uart_page_498680(g2_nav_max_map_img_2007477c, NULL);
            audio_uart_page_498680(g2_nav_a_compass_img_200747e8, NULL);
            /* Drop every received record. */
            (void)osMutexAcquire(g2_navigation_mutex, 0xffffffffu);
            g2_nav_var_20074758 = 0u;
            (void)aeabi_memset_43c0e4(&g2_navigation_location_list_20376c38, 0x55c, 0);
            (void)aeabi_memset_43c0e4(&g2_navigation_info_staging_2037bdd0, 0x18c, 0);
            (void)aeabi_memset_43c0e4(g2_nav_buf_20329600, 0x4674, 0);
            (void)aeabi_memset_43c0e4(g2_nav_buf_202e4fc8, 0xea7c, 0);
            (void)osMutexRelease(g2_navigation_mutex);
        }
        if (cmd == NAV_CMD_SYSTEM_EXIT)
            nav_system_exit(0xae6u);
        break;

    case NAV_STATE_EXIT_PAGE:
        nav_exit_page_state(cmd, input, 0xb06u, 0xb0cu);
        break;
    case NAV_STATE_7:
        nav_exit_page_state(cmd, input, 0xb28u, 0xb2fu);
        break;
    case NAV_STATE_BREAK_EXIT:
        nav_exit_page_state(cmd, input, 0xb4cu, 0xb52u);
        break;

    default:
        NAV_LOG(2u, 0xb5cu, 0x08400000u, msg_unknown_state, (uint32_t)g2_navigation_ui_state_20074fed);
        break;
    }
    return 0;
}
