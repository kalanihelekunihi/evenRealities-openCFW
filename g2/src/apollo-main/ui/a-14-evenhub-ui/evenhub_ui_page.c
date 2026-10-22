/* EvenHub page build and refresh, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_ui.c.
 * Native 0x494834..0x4949ae (evenhub_ui_create_root_container), 0x494bec..0x495f9a
 * (evenhub_ui_page_create, evenhub_ui_page_rebuild, the three pb->config converters),
 * 0x496430..0x4964ca (evenhub_ui_create_timeout_exit_page) and 0x496544..0x49718c
 * (evenhub_ui_reflash_event_handler); literal pools 0x494bd8..0x494bec, 0x4954c4..0x4955b4,
 * 0x495e44..0x495e84, 0x49619c..0x4961e4, 0x4963e8..0x496430, 0x49652c..0x496544 and
 * 0x49718c..0x49729c.
 *
 * The phone app sends one protobuf message (decoded into the 0x3758-byte g2_evenhub_rx_msg);
 * page_create/page_rebuild build list/text/image containers from it and bind the first
 * container with Is_event_capture=1 to the input path. Every request is answered with
 * evenhub_send_reply_4d9c86(cmd, seq, which, status). */
#include "evenhub_ui_private.h"

#define EVENHUB_APP_ID 0xe0u
#define EVENHUB_EXIT_RECORD_KEY 0x40102u
#define EVENHUB_ROLE_MASTER 1u

/* Message commands (msg.cmd) and their which_Msg_Ctx values. */
#define EVENHUB_CMD_TEXT_UPGRADE 5u
#define EVENHUB_CMD_REBUILD 7u
#define EVENHUB_CMD_SHUTDOWN 9u
#define EVENHUB_CMD_PRIVATE_EVENT 0xbu
#define EVENHUB_CMD_AUDIO_CTRL_ACK 0xcu
#define EVENHUB_CMD_TIMEOUT_PAGE 0xeu
#define EVENHUB_CMD_AUDIO_CTRL 0xfu
#define EVENHUB_WHICH_TEXT_UPGRADE 9u
#define EVENHUB_WHICH_SHUTDOWN 0xbu
#define EVENHUB_WHICH_PRIVATE_EVENT 0x10u
#define EVENHUB_WHICH_AUDIO_CTRL_ACK 0xeu
#define EVENHUB_WHICH_AUDIO_CTRL 0x12u

#define EVENHUB_EVENT_CLICK 10
#define EVENHUB_EVENT_SCROLL_UP 0x44
#define EVENHUB_EVENT_SCROLL_DOWN 0x45
#define EVENHUB_EVENT_IMAGE_REFRESH 0x4c

#define EVENHUB_COMPRESS_NONE 0u
#define EVENHUB_COMPRESS_RLE 1u
#define EVENHUB_COMPRESS_LZ4 2u

#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_ALIGN_CENTER 9u
#define LV_OPA_COVER 0xffu

/* LVGL 9 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f506(void *obj, int32_t w);                       /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                       /* lv_obj_set_height */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);                  /* lv_obj_set_align */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);         /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);         /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);         /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);         /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);    /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);         /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);         /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);         /* shadow_width */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);         /* shadow_spread */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);      /* text_opa */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);     /* text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);         /* radius */
extern void audio_uart_page_44d878(void *obj);                                  /* lv_obj_clean */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *label, uint32_t text);                 /* lv_label_set_text */
extern void evenhub_obj_set_style_pad_all_4935cc(void *obj, int32_t v, uint32_t sel); /* pad l/r/t/b */
extern uint32_t audio_uart_ring_primary_head_cell; /* RAM 0x200746dc: active lv_font_t * */

/* i18n. */
extern uint32_t audio_uart_page_460084(const char *key);                 /* i18n index of key */
extern uint32_t audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */

/* Common containers. */
extern int32_t common_list_container_inject_event_4de354(void *list, uint8_t event);
extern int32_t common_text_container_inject_event_4e033c(void *text, uint8_t event, uint32_t hi,
                                                         uint32_t lo);
extern int32_t common_image_container_set_data_4dc5ae(void *image, const void *data, uint32_t len);

/* EvenHub main / data parser. */
extern void evenhub_main_exit_pending_set_4e0ca0(void);        /* RAM 0x200745c4 = 1 */
extern void evenhub_main_shutdown_state_set_4e0cb2(uint32_t v); /* RAM 0x200745b8 = v */
extern void evenhub_main_audio_ack_clear_4e0cba(void);         /* RAM 0x200745ac = 0 */
extern void evenhub_main_timeout_page_set_4e0cc4(void);        /* RAM byte 0x20074fc4 = 1 */
extern uint32_t evenhub_lz4_decompress_4e0c0c(const void *src, uint32_t src_len, void *dst,
                                              uint32_t dst_cap); /* 0 on failure */
extern uint32_t evenhub_rle_decompress_4e0c34(const void *src, uint32_t src_len, void *dst,
                                              uint32_t dst_cap); /* {count, byte} pairs */
extern uint8_t evenhub_audio_acquire_set_4e1406(uint32_t on);  /* AUDM app 5 acquire/release */
extern int32_t evenhub_send_audio_ctrl_ack_4d9bfe(uint8_t seq, uint8_t cmd, uint32_t value);
extern int32_t evenhub_send_audio_ctrl_reply_4da56e(uint8_t seq, uint8_t state);

/* System. */
extern void Common_Fadeout_Anim_Start_4641b6(void *object, uint32_t app);
extern void system_close_page_factory_0046ae9c(uint32_t, uint32_t);
extern void audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                            uint32_t context);
extern int32_t audio_uart_handshake_send(uint32_t channel, const void *bytes, uint32_t size,
                                         uint32_t flags, uint32_t command); /* 0x465480 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern void *file_heap_allocate(uint32_t size); /* 0x474cd2 */
extern void file_heap_free(void *buffer);       /* 0x474d16 */

/* Usage record for key 0x40102: {startup widget id, 2}. */
typedef struct {
    uint32_t widget;
    uint32_t source;
} evenhub_exit_record_t;
extern const evenhub_exit_record_t g2_evenhub_exit_record_init; /* ROM 0x78d5e4 = {0, 2} */

static const char evenhub_ui_tag[] = "evenhub.ui"; /* ROM 0x78aa24 */
static const char evenhub_ui_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_ui.c"; /* ROM 0x702a54 */

static const char root_fn[] = "evenhub_ui_create_root_container"; /* ROM 0x754698 */
static const char root_null[] =
    "evenhub_ui_create_root_container manager_ctx_ptr or parent_obj is NULL"; /* ROM 0x6fa8d4 */
static const char root_null_s[] =
    "[evenhub.ui]evenhub_ui_create_root_container manager_ctx_ptr or parent_obj is NULL"; /* ROM 0x6e7f60 */
static const char root_fail[] = "evenhub_ui_create_root_container create failed"; /* ROM 0x7340f4 */
static const char root_fail_s[] = "[evenhub.ui]evenhub_ui_create_root_container create failed"; /* ROM 0x715304 */

static const char create_fn[] = "evenhub_ui_page_create";   /* ROM 0x77760c (__func__) */
static const char rebuild_fn[] = "evenhub_ui_page_rebuild"; /* ROM 0x77763c (__func__) */
/* page_rebuild logs with the page_create messages. */
static const char pc_enter[] = "evenhub_ui_page_create"; /* ROM 0x777624 */
static const char pc_enter_s[] = "[evenhub.ui]evenhub_ui_page_create"; /* ROM 0x7546bc */
static const char pc_null[] = "evenhub_ui_page_create manager_ctx is NULL"; /* ROM 0x73ed6c */
static const char pc_null_s[] = "[evenhub.ui]evenhub_ui_page_create manager_ctx is NULL"; /* ROM 0x71efb0 */
static const char pc_nodata[] = "evenhub_ui_page_create data is NULL or length is 0"; /* ROM 0x729934 */
static const char pc_nodata_s[] =
    "[evenhub.ui]evenhub_ui_page_create data is NULL or length is 0"; /* ROM 0x70b9e4 */
static const char pc_none[] = "(none)"; /* ROM 0x78d5dc */
static const char pc_decode[] = "evenhub protobuf decode failed: %s\n"; /* ROM 0x7546e0 */
static const char pc_decode_s[] = "[evenhub.ui]evenhub protobuf decode failed: %s\n"; /* ROM 0x734184 */
static const char pc_widget[] = "evenhub_ui_page_create: startup widget id is %d"; /* ROM 0x7341b4 */
static const char pc_widget_s[] = "[evenhub.ui]evenhub_ui_page_create: startup widget id is %d"; /* ROM 0x7153f4 */
static const char pc_list_fail[] = "evenhub_ui_page_create: create container list failed"; /* ROM 0x71efe8 */
static const char pc_list_fail_s[] =
    "[evenhub.ui]evenhub_ui_page_create: create container list failed"; /* ROM 0x702cb8 */
static const char pc_list_ok[] =
    "evenhub_ui_page_create: container list created successfully, count=%d"; /* ROM 0x6fa964 */
static const char pc_list_ok_s[] =
    "[evenhub.ui]evenhub_ui_page_create: container list created successfully, count=%d"; /* ROM 0x6e7fb4 */
static const char pc_traverse[] = "evenhub_ui_page_create: traversing container list:"; /* ROM 0x729968 */
static const char pc_traverse_s[] =
    "[evenhub.ui]evenhub_ui_page_create: traversing container list:"; /* ROM 0x70ba24 */
static const char pc_creating[] = "evenhub_ui_page_create: creating UI containers from PB data..."; /* ROM 0x70ba64 */
static const char pc_creating_s[] =
    "[evenhub.ui]evenhub_ui_page_create: creating UI containers from PB data..."; /* ROM 0x6f3778 */
static const char pc_unknown[] = "evenhub_ui_page_create: unknown container type %d"; /* ROM 0x72999c */
static const char pc_unknown_s[] = "[evenhub.ui]evenhub_ui_page_create: unknown container type %d"; /* ROM 0x70bb24 */
static const char pc_img_ok[] =
    "evenhub_ui_page_create: Image container created successfully (handle=%p)"; /* ROM 0x6f385c */
static const char pc_img_ok_s[] =
    "[evenhub.ui]evenhub_ui_page_create: Image container created successfully (handle=%p)"; /* ROM 0x6e34b8 */
static const char pc_list_new[] = "evenhub_ui_page_create: creating List container (ID=%u, Name=%s)"; /* ROM 0x702cfc */
static const char pc_list_new_s[] =
    "[evenhub.ui]evenhub_ui_page_create: creating List container (ID=%u, Name=%s)"; /* ROM 0x6ed428 */
static const char pc_lc_ok[] =
    "evenhub_ui_page_create: List container created successfully (handle=%p)"; /* ROM 0x6fa9ac */
static const char pc_lc_ok_s[] =
    "[evenhub.ui]evenhub_ui_page_create: List container created successfully (handle=%p)"; /* ROM 0x6e8008 */
static const char pc_lc_bound[] = "evenhub_ui_page_create: List container bound to events"; /* ROM 0x71f020 */
static const char pc_lc_bound_s[] =
    "[evenhub.ui]evenhub_ui_page_create: List container bound to events"; /* ROM 0x702d40 */
static const char pc_lc_nobind[] = "evenhub_ui_page_create: failed to bind List container events"; /* ROM 0x70baa4 */
static const char pc_lc_nobind_s[] =
    "[evenhub.ui]evenhub_ui_page_create: failed to bind List container events"; /* ROM 0x6f37c4 */
static const char pc_lc_fail[] = "evenhub_ui_page_create: failed to create List container"; /* ROM 0x71f058 */
static const char pc_lc_fail_s[] =
    "[evenhub.ui]evenhub_ui_page_create: failed to create List container"; /* ROM 0x702d84 */
static const char pc_text_new[] = "evenhub_ui_page_create: creating Text container (ID=%u, Name=%s)"; /* ROM 0x702dc8 */
static const char pc_text_new_s[] =
    "[evenhub.ui]evenhub_ui_page_create: creating Text container (ID=%u, Name=%s)"; /* ROM 0x6ed478 */
static const char pc_tc_ok[] =
    "evenhub_ui_page_create: Text container created successfully (handle=%p)"; /* ROM 0x6fa9f4 */
static const char pc_tc_ok_s[] =
    "[evenhub.ui]evenhub_ui_page_create: Text container created successfully (handle=%p)"; /* ROM 0x6e805c */
static const char pc_tc_bound[] = "evenhub_ui_page_create: Text container bound to events"; /* ROM 0x71f090 */
static const char pc_tc_bound_s[] =
    "[evenhub.ui]evenhub_ui_page_create: Text container bound to events"; /* ROM 0x702e0c */
static const char pc_tc_nobind[] = "evenhub_ui_page_create: failed to bind Text container events"; /* ROM 0x70bae4 */
static const char pc_tc_nobind_s[] =
    "[evenhub.ui]evenhub_ui_page_create: failed to bind Text container events"; /* ROM 0x6f3810 */
static const char pc_tc_fail[] = "evenhub_ui_page_create: failed to create Text container"; /* ROM 0x71f0c8 */
static const char pc_tc_fail_s[] =
    "[evenhub.ui]evenhub_ui_page_create: failed to create Text container"; /* ROM 0x702e50 */
static const char pc_img_new[] = "evenhub_ui_page_create: creating Image container (ID=%u, Name=%s)"; /* ROM 0x702e94 */
static const char pc_img_new_s[] =
    "[evenhub.ui]evenhub_ui_page_create: creating Image container (ID=%u, Name=%s)"; /* ROM 0x6ed4c8 */
static const char pc_img_fail[] = "evenhub_ui_page_create: failed to create Image container"; /* ROM 0x715430 */
static const char pc_img_fail_s[] =
    "[evenhub.ui]evenhub_ui_page_create: failed to create Image container"; /* ROM 0x6faa3c */
static const char pc_no_capture[] =
    "evenhub_ui_page_create: no container with Is_event_capture=1 found or binding failed"; /* ROM 0x6e3510 */
static const char pc_no_capture_s[] =
    "[evenhub.ui]evenhub_ui_page_create: no container with Is_event_capture=1 found or binding failed"; /* ROM 0x6da8cc */

static const char tmo_fn[] = "evenhub_ui_create_timeout_exit_page"; /* ROM 0x75474c */
static const char tmo_msg[] = "navigation_ui_create_break_exit_page"; /* ROM 0x74a104 */
static const char tmo_msg_s[] = "[evenhub.ui]navigation_ui_create_break_exit_page"; /* ROM 0x7299d0 */
static const char tmo_text_key[] = "ID_GENERAL_BLUETOOTH_DISCONNECT"; /* ROM 0x760070 */

static const char rf_fn[] = "evenhub_ui_reflash_event_handler"; /* ROM 0x754770 */
static const char rf_enter[] = "evenhub_ui_page reflash event handler"; /* ROM 0x74a12c */
static const char rf_enter_s[] = "[evenhub.ui]evenhub_ui_page reflash event handler"; /* ROM 0x729a04 */
static const char rf_private[] = "evenhub_ui_reflash_event_handler: receive private event packet"; /* ROM 0x70bba4 */
static const char rf_private_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: receive private event packet"; /* ROM 0x6f38f4 */
static const char rf_found[] = "evenhub_ui_reflash_event_handler: container_id=%u found"; /* ROM 0x71f170 */
static const char rf_found_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: container_id=%u found"; /* ROM 0x702f60 */
static const char rf_image[] = "evenhub_ui_reflash_event_handler: receive image refresh event"; /* ROM 0x70bbe4 */
static const char rf_image_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: receive image refresh event"; /* ROM 0x6f3940 */
static const char rf_alloc[] = "evenhub_ui: alloc decode buffer failed (%u bytes)"; /* ROM 0x729a38 */
static const char rf_alloc_s[] = "[evenhub.ui]evenhub_ui: alloc decode buffer failed (%u bytes)"; /* ROM 0x70bc24 */
static const char rf_unz_fail[] = "evenhub_ui: decompress failed, mode=%u raw_len=%u"; /* ROM 0x729a6c */
static const char rf_unz_fail_s[] = "[evenhub.ui]evenhub_ui: decompress failed, mode=%u raw_len=%u"; /* ROM 0x70bc64 */
static const char rf_unz_ok[] = "evenhub_ui: decompress mode=%u %u -> %u bytes"; /* ROM 0x7342a4 */
static const char rf_unz_ok_s[] = "[evenhub.ui]evenhub_ui: decompress mode=%u %u -> %u bytes"; /* ROM 0x715598 */
static const char rf_unz_mode[] = "evenhub_ui: unsupported compress mode %u, treat as raw"; /* ROM 0x71f1a8 */
static const char rf_unz_mode_s[] =
    "[evenhub.ui]evenhub_ui: unsupported compress mode %u, treat as raw"; /* ROM 0x702fa4 */
static const char rf_img_ok[] = "evenhub_ui_reflash_event_handler: set image data success"; /* ROM 0x7155d4 */
static const char rf_img_ok_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: set image data success"; /* ROM 0x6faacc */
static const char rf_img_fail[] = "evenhub_ui_reflash_event_handler: set image data failed, ret=%d"; /* ROM 0x70bca4 */
static const char rf_img_fail_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: set image data failed, ret=%d"; /* ROM 0x6f398c */
static const char rf_bad_event[] = "evenhub_ui_reflash_event_handler: unknown event id=%d"; /* ROM 0x71f1e0 */
static const char rf_bad_event_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: unknown event id=%d"; /* ROM 0x702fe8 */
static const char rf_missing[] = "evenhub_ui_reflash_event_handler: container_id=%u not found"; /* ROM 0x715610 */
static const char rf_missing_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: container_id=%u not found"; /* ROM 0x6fab14 */
static const char rf_shutdown[] = "evenhub_ui_reflash_event_handler: is shutdown process en, return 0"; /* ROM 0x70302c */
static const char rf_shutdown_s[] =
    "[evenhub.ui]evenhub_ui_reflash_event_handler: is shutdown process en, return 0"; /* ROM 0x6ed518 */
static const char rf_rebuild_fail[] = "evenhub_ui_page_create: rebuild page failed"; /* ROM 0x73ed98 */
static const char rf_rebuild_fail_s[] = "[evenhub.ui]evenhub_ui_page_create: rebuild page failed"; /* ROM 0x71f218 */
static const char rf_master[] =
    "evenhub_ui_event_handler rebuild page failed, current role is MASTER_ROLE, request display stop"; /* ROM 0x6dd414 */
static const char rf_master_s[] =
    "[evenhub.ui]evenhub_ui_event_handler rebuild page failed, current role is MASTER_ROLE, request display stop"; /* ROM 0x6ca9d4 */
static const char rf_slave[] =
    "evenhub_ui_event_handler rebuild page failed, current role is SLAVE_ROLE, send abnormal exit event to master"; /* ROM 0x6d70b0 */
static const char rf_slave_s[] =
    "[evenhub.ui]evenhub_ui_event_handler rebuild page failed, current role is SLAVE_ROLE, send abnormal exit event to master"; /* ROM 0x64e1ac */
static const char rf_tmo_enter[] = "evenhub_ui_page_create: receive system enter timeout page event"; /* ROM 0x70bce4 */
static const char rf_tmo_enter_s[] =
    "[evenhub.ui]evenhub_ui_page_create: receive system enter timeout page event"; /* ROM 0x6f39d8 */
static const char rf_tmo_exit[] = "evenhub_ui_page_create: receive system timeout page exit event"; /* ROM 0x70bd24 */
static const char rf_tmo_exit_s[] =
    "[evenhub.ui]evenhub_ui_page_create: receive system timeout page exit event"; /* ROM 0x6f3a24 */
static const char rf_text[] = "evenhub_ui_page_create: receive text upgrade packet from APP"; /* ROM 0x70bd64 */
static const char rf_text_s[] =
    "[evenhub.ui]evenhub_ui_page_create: receive text upgrade packet from APP"; /* ROM 0x6f3a70 */
static const char rf_text_ok[] = "evenhub_ui_page_create: update text content success"; /* ROM 0x729aa0 */
static const char rf_text_ok_s[] = "[evenhub.ui]evenhub_ui_page_create: update text content success"; /* ROM 0x70bda4 */
static const char rf_text_missing[] = "evenhub_ui_page_create: container_id=%u not found"; /* ROM 0x729ad4 */
static const char rf_text_missing_s[] = "[evenhub.ui]evenhub_ui_page_create: container_id=%u not found"; /* ROM 0x70bde4 */
static const char rf_which[] = "evenhub_ui_page_create: unknown which_Msg_Ctx=%d"; /* ROM 0x729b08 */
static const char rf_which_s[] = "[evenhub.ui]evenhub_ui_page_create: unknown which_Msg_Ctx=%d"; /* ROM 0x70be24 */
static const char rf_shut[] = "evenhub_ui_page_create: receive shutdown packet from APP"; /* ROM 0x71564c */
static const char rf_shut_s[] = "[evenhub.ui]evenhub_ui_page_create: receive shutdown packet from APP"; /* ROM 0x6fab5c */
static const char rf_exit_now[] = "evenhub_ui_page_create: exit immediately"; /* ROM 0x73edc4 */
static const char rf_exit_now_s[] = "[evenhub.ui]evenhub_ui_page_create: exit immediately"; /* ROM 0x71f250 */
static const char rf_popup[] = "evenhub_ui_page_create: pop up foreground layer program"; /* ROM 0x71f288 */
static const char rf_popup_s[] =
    "[evenhub.ui]evenhub_ui_page_create: pop up foreground layer program"; /* ROM 0x703070 */
static const char rf_audio[] =
    "evenhub_ui_page_create: receive audio control packet from APP ,value=%d"; /* ROM 0x6faba4 */
static const char rf_audio_s[] =
    "[evenhub.ui]evenhub_ui_page_create: receive audio control packet from APP ,value=%d"; /* ROM 0x6e80b0 */
static const char rf_cmd[] = "evenhub_ui_page_create: unknown cmd=%d"; /* ROM 0x74a154 */
static const char rf_cmd_s[] = "[evenhub.ui]evenhub_ui_page_create: unknown cmd=%d"; /* ROM 0x729b3c */

/* Full-screen (576x288) transparent-styled black root with white text and no padding. */
void *evenhub_ui_create_root_container_494834(void *parent)
{
    void *obj;

    if (parent == NULL) {
        EH_LOG(1, root_fn, 0x2ec, 0x4000000u, root_null, root_null_s);
        return NULL;
    }
    obj = audio_uart_page_43de82(parent);
    if (obj == NULL) {
        EH_LOG(1, root_fn, 0x2f1, 0x4000000u, root_fail, root_fail_s);
        return NULL;
    }
    audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f506(obj, 0x240);
    audio_uart_page_43f568(obj, 0x120);
    audio_uart_page_43f09a(obj, 0, 0);
    audio_uart_page_43dfa4(obj, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44127e(obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(obj, LV_OPA_COVER, 0u);
    audio_uart_page_44140e(obj, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(obj, LV_OPA_COVER, 0u);
    audio_uart_page_4412ec(obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44131c(obj, 0, 0u);
    audio_uart_page_44133a(obj, 0, 0u);
    audio_uart_page_441378(obj, 0, 0u);
    audio_uart_page_441386(obj, 0, 0u);
    audio_uart_page_4413b0(obj, 0, 0u);
    audio_uart_page_44146a(obj, 0, 0u);
    evenhub_obj_set_style_pad_all_4935cc(obj, 0, 0u);
    audio_uart_page_44120e(obj, 0, 0u);
    audio_uart_page_44121c(obj, 0, 0u);
    audio_uart_page_44122a(obj, 0, 0u);
    audio_uart_page_441238(obj, 0, 0u);
    return obj;
}

/* Returns 0, -1 (bad args / decode), -2 (container list) or -3 (container creation). */
int32_t evenhub_ui_page_create_494bec(const void *data, int16_t len, evenhub_manager_t *mgr)
{
    evenhub_msg_t *msg = &g2_evenhub_rx_msg;
    evenhub_pb_istream_t stream;
    evenhub_image_config_t image_cfg;
    evenhub_text_config_t text_cfg;
    evenhub_list_config_t list_cfg;
    evenhub_container_node_t *node;
    void *handle;
    bool bound;

    EH_LOG(4, create_fn, 0x32c, 0x10000000u, pc_enter, pc_enter_s);
    g2_evenhub_startup_widget_id = 0u;
    if (mgr == NULL) {
        EH_LOG(1, create_fn, 0x331, 0x4000000u, pc_null, pc_null_s);
        return -1;
    }
    if (data == NULL || len == 0) {
        EH_LOG(1, create_fn, 0x336, 0x4000000u, pc_nodata, pc_nodata_s);
        return -1;
    }
    audio_uart_buffer_zero(msg, EVENHUB_MSG_SIZE, 0u);
    stream = audio_uart_pb_stream_init(data, (uint32_t)len);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_evenhub_pb_msg_fields_77754c, msg) == 0u) {
        EH_LOG(1, create_fn, 0x33e, 0x4400000u, pc_decode, pc_decode_s,
               (stream.errmsg != NULL) ? stream.errmsg : pc_none);
        (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 3u);
        return -1;
    }
    g2_evenhub_startup_widget_id = EVENHUB_MSG_STARTUP_WIDGET(msg);
    EH_LOG(3, create_fn, 0x347, 0xc400000u, pc_widget, pc_widget_s, g2_evenhub_startup_widget_id);
    if (evenhub_container_list_create_from_pb_493bdc(mgr, &msg->value) != 0) {
        EH_LOG(1, create_fn, 0x34a, 0x4000000u, pc_list_fail, pc_list_fail_s);
        (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 3u);
        return -2;
    }
    EH_LOG(3, create_fn, 0x351, 0xc400000u, pc_list_ok, pc_list_ok_s, mgr->count);
    EH_LOG(4, create_fn, 0x354, 0x10000000u, pc_traverse, pc_traverse_s);
    (void)evenhub_container_list_traverse_493ee6(mgr, evenhub_print_container_info_callback_4940e8,
                                                 NULL);
    EH_LOG(4, create_fn, 0x358, 0x10000000u, pc_creating, pc_creating_s);

    bound = false;
    for (node = mgr->head; node != NULL; node = node->next) {
        switch (node->type) {
        case EVENHUB_CONTAINER_LIST: {
            const evenhub_pb_list_t *pb = (const evenhub_pb_list_t *)node->pb;

            EH_LOG(4, create_fn, 0x361, 0x10800000u, pc_list_new, pc_list_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&list_cfg, sizeof(list_cfg), 0u);
            evenhub_list_config_from_pb_495e84(pb, &list_cfg);
            handle = common_list_container_create_4dd510(mgr->parent, &list_cfg,
                                                         (void *)common_list_event_callback_4949c0,
                                                         mgr);
            if (handle == NULL) {
                EH_LOG(1, create_fn, 0x38a, 0x4000000u, pc_lc_fail, pc_lc_fail_s);
                (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 1u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, create_fn, 0x374, 0xc400000u, pc_lc_ok, pc_lc_ok_s, handle);
            if (pb->is_event_capture == 1u && !bound) {
                if (evenhub_bind_event_container_4942a4(mgr, handle,
                                                        evenhub_list_event_inject_adapter_495f9a,
                                                        pb->id, pb->name,
                                                        EVENHUB_CONTAINER_LIST, mgr) == 0) {
                    bound = true;
                    EH_LOG(3, create_fn, 900, 0xc000000u, pc_lc_bound, pc_lc_bound_s);
                } else {
                    EH_LOG(1, create_fn, 0x386, 0x4000000u, pc_lc_nobind, pc_lc_nobind_s);
                }
            }
            break;
        }
        case EVENHUB_CONTAINER_TEXT: {
            const evenhub_pb_text_t *pb = (const evenhub_pb_text_t *)node->pb;

            EH_LOG(4, create_fn, 0x396, 0x10800000u, pc_text_new, pc_text_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&text_cfg, sizeof(text_cfg), 0u);
            evenhub_text_config_from_pb_495f1a(pb, &text_cfg);
            handle = common_text_container_create_4dee96(mgr->parent, &text_cfg,
                                                         (void *)common_text_event_callback_494a78,
                                                         mgr);
            if (handle == NULL) {
                EH_LOG(1, create_fn, 0x3bf, 0x4000000u, pc_tc_fail, pc_tc_fail_s);
                (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 1u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, create_fn, 0x3a9, 0xc400000u, pc_tc_ok, pc_tc_ok_s, handle);
            if (pb->is_event_capture == 1u && !bound) {
                if (evenhub_bind_event_container_4942a4(mgr, handle,
                                                        evenhub_text_event_inject_adapter_4961e4,
                                                        pb->id, pb->name,
                                                        EVENHUB_CONTAINER_TEXT, mgr) == 0) {
                    bound = true;
                    EH_LOG(3, create_fn, 0x3b9, 0xc000000u, pc_tc_bound, pc_tc_bound_s);
                } else {
                    EH_LOG(1, create_fn, 0x3bb, 0x4000000u, pc_tc_nobind, pc_tc_nobind_s);
                }
            }
            break;
        }
        case EVENHUB_CONTAINER_IMAGE: {
            const evenhub_pb_image_t *pb = (const evenhub_pb_image_t *)node->pb;

            EH_LOG(4, create_fn, 0x3cb, 0x10800000u, pc_img_new, pc_img_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&image_cfg, sizeof(image_cfg), 0u);
            evenhub_image_config_from_pb_495f6a(pb, &image_cfg);
            handle = common_image_container_create_4dbede(mgr->parent, &image_cfg);
            if (handle == NULL) {
                EH_LOG(1, create_fn, 0x3e0, 0x4000000u, pc_img_fail, pc_img_fail_s);
                (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 1u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, create_fn, 0x3dc, 0xc400000u, pc_img_ok, pc_img_ok_s, handle);
            break;
        }
        default:
            EH_LOG(2, create_fn, 0x3e9, 0x8400000u, pc_unknown, pc_unknown_s, node->type);
            break;
        }
    }
    if (!bound)
        EH_LOG(2, create_fn, 0x3f1, 0x8000000u, pc_no_capture, pc_no_capture_s);
    (void)evenhub_send_reply_4d9c86(1u, msg->seq, 4u, 0u);
    return 0;
}

/* Same as page_create for an already running page (cmd 7): rebuilds the container list in
 * place, keeps the startup widget id, replies (8, seq, 8, 6 ok / 7 fail). Returns 0, -1 or -3. */
int32_t evenhub_ui_page_rebuild_4955b4(const void *data, int16_t len, evenhub_manager_t *mgr)
{
    evenhub_msg_t *msg = &g2_evenhub_rx_msg;
    evenhub_pb_istream_t stream;
    evenhub_image_config_t image_cfg;
    evenhub_text_config_t text_cfg;
    evenhub_list_config_t list_cfg;
    evenhub_container_node_t *node;
    void *handle;
    bool bound;

    EH_LOG(4, rebuild_fn, 0x3fc, 0x10000000u, pc_enter, pc_enter_s);
    if (mgr == NULL) {
        EH_LOG(1, rebuild_fn, 0x400, 0x4000000u, pc_null, pc_null_s);
        return -1;
    }
    if (data == NULL || len == 0) {
        EH_LOG(1, rebuild_fn, 0x405, 0x4000000u, pc_nodata, pc_nodata_s);
        return -1;
    }
    audio_uart_buffer_zero(msg, EVENHUB_MSG_SIZE, 0u);
    stream = audio_uart_pb_stream_init(data, (uint32_t)len);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_evenhub_pb_msg_fields_77754c, msg) == 0u) {
        EH_LOG(1, rebuild_fn, 0x40d, 0x4400000u, pc_decode, pc_decode_s,
               (stream.errmsg != NULL) ? stream.errmsg : pc_none);
        (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 7u);
        return -1;
    }
    if (evenhub_container_list_rebuild_from_pb_493ab6(mgr, &msg->value) != 0) {
        EH_LOG(1, rebuild_fn, 0x417, 0x4000000u, pc_list_fail, pc_list_fail_s);
        (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 7u);
        return -1;
    }
    EH_LOG(3, rebuild_fn, 0x41e, 0xc400000u, pc_list_ok, pc_list_ok_s, mgr->count);
    EH_LOG(4, rebuild_fn, 0x421, 0x10000000u, pc_traverse, pc_traverse_s);
    (void)evenhub_container_list_traverse_493ee6(mgr, evenhub_print_container_info_callback_4940e8,
                                                 NULL);
    EH_LOG(4, rebuild_fn, 0x425, 0x10000000u, pc_creating, pc_creating_s);

    bound = false;
    for (node = mgr->head; node != NULL; node = node->next) {
        switch (node->type) {
        case EVENHUB_CONTAINER_LIST: {
            const evenhub_pb_list_t *pb = (const evenhub_pb_list_t *)node->pb;

            EH_LOG(4, rebuild_fn, 0x42e, 0x10800000u, pc_list_new, pc_list_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&list_cfg, sizeof(list_cfg), 0u);
            evenhub_list_config_from_pb_495e84(pb, &list_cfg);
            handle = common_list_container_create_4dd510(mgr->parent, &list_cfg,
                                                         (void *)common_list_event_callback_4949c0,
                                                         mgr);
            if (handle == NULL) {
                EH_LOG(1, rebuild_fn, 0x457, 0x4000000u, pc_lc_fail, pc_lc_fail_s);
                (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 7u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, rebuild_fn, 0x441, 0xc400000u, pc_lc_ok, pc_lc_ok_s, handle);
            if (pb->is_event_capture == 1u && !bound) {
                if (evenhub_bind_event_container_4942a4(mgr, handle,
                                                        evenhub_list_event_inject_adapter_495f9a,
                                                        pb->id, pb->name,
                                                        EVENHUB_CONTAINER_LIST, mgr) == 0) {
                    bound = true;
                    EH_LOG(3, rebuild_fn, 0x451, 0xc000000u, pc_lc_bound, pc_lc_bound_s);
                } else {
                    EH_LOG(1, rebuild_fn, 0x453, 0x4000000u, pc_lc_nobind, pc_lc_nobind_s);
                }
            }
            break;
        }
        case EVENHUB_CONTAINER_TEXT: {
            const evenhub_pb_text_t *pb = (const evenhub_pb_text_t *)node->pb;

            EH_LOG(4, rebuild_fn, 0x462, 0x10800000u, pc_text_new, pc_text_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&text_cfg, sizeof(text_cfg), 0u);
            evenhub_text_config_from_pb_495f1a(pb, &text_cfg);
            handle = common_text_container_create_4dee96(mgr->parent, &text_cfg,
                                                         (void *)common_text_event_callback_494a78,
                                                         mgr);
            if (handle == NULL) {
                EH_LOG(1, rebuild_fn, 0x48b, 0x4000000u, pc_tc_fail, pc_tc_fail_s);
                (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 7u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, rebuild_fn, 0x475, 0xc400000u, pc_tc_ok, pc_tc_ok_s, handle);
            if (pb->is_event_capture == 1u && !bound) {
                if (evenhub_bind_event_container_4942a4(mgr, handle,
                                                        evenhub_text_event_inject_adapter_4961e4,
                                                        pb->id, pb->name,
                                                        EVENHUB_CONTAINER_TEXT, mgr) == 0) {
                    bound = true;
                    EH_LOG(3, rebuild_fn, 0x485, 0xc000000u, pc_tc_bound, pc_tc_bound_s);
                } else {
                    EH_LOG(1, rebuild_fn, 0x487, 0x4000000u, pc_tc_nobind, pc_tc_nobind_s);
                }
            }
            break;
        }
        case EVENHUB_CONTAINER_IMAGE: {
            const evenhub_pb_image_t *pb = (const evenhub_pb_image_t *)node->pb;

            EH_LOG(4, rebuild_fn, 0x496, 0x10800000u, pc_img_new, pc_img_new_s, pb->id, pb->name);
            audio_uart_buffer_zero(&image_cfg, sizeof(image_cfg), 0u);
            evenhub_image_config_from_pb_495f6a(pb, &image_cfg);
            handle = common_image_container_create_4dbede(mgr->parent, &image_cfg);
            if (handle == NULL) {
                EH_LOG(1, rebuild_fn, 0x4ab, 0x4000000u, pc_img_fail, pc_img_fail_s);
                (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 7u);
                return -3;
            }
            node->ui = handle;
            EH_LOG(3, rebuild_fn, 0x4a7, 0xc400000u, pc_img_ok, pc_img_ok_s, handle);
            break;
        }
        default:
            EH_LOG(2, rebuild_fn, 0x4b4, 0x8400000u, pc_unknown, pc_unknown_s, node->type);
            break;
        }
    }
    if (!bound)
        EH_LOG(2, rebuild_fn, 0x4bc, 0x8000000u, pc_no_capture, pc_no_capture_s);
    (void)evenhub_send_reply_4d9c86(8u, msg->seq, 8u, 6u);
    return 0;
}

void evenhub_list_config_from_pb_495e84(const evenhub_pb_list_t *pb, evenhub_list_config_t *cfg)
{
    uint32_t i;

    if (pb == NULL || cfg == NULL)
        return;
    cfg->x = pb->x;
    cfg->y = pb->y;
    cfg->width = pb->width;
    cfg->height = pb->height;
    cfg->padding = pb->padding;
    cfg->border_width = pb->border_width;
    cfg->border_color = pb->border_color;
    cfg->border_radius = pb->border_radius;
    if (pb->has_items == 0u) {
        cfg->item_count = 0u;
        cfg->item_width = 0u;
        cfg->select_border = 0u;
        return;
    }
    cfg->item_count = pb->item_count;
    cfg->item_width = pb->item_width;
    cfg->select_border = (pb->select_border != 0u);
    for (i = 0u; i < cfg->item_count && (int32_t)i < 20 && (int32_t)i < (int32_t)pb->item_name_count;
         i++) {
        (void)audio_settings_copy_text(cfg->item_name[i], pb->item_name[i], 0x3fu);
        cfg->item_name[i][0x3f] = '\0';
    }
}

void evenhub_text_config_from_pb_495f1a(const evenhub_pb_text_t *pb, evenhub_text_config_t *cfg)
{
    if (pb == NULL || cfg == NULL)
        return;
    cfg->x = (int16_t)pb->x;
    cfg->y = (int16_t)pb->y;
    cfg->width = (int16_t)pb->width;
    cfg->height = (int16_t)pb->height;
    cfg->border_width = (uint8_t)pb->border_width;
    cfg->border_color = (uint8_t)pb->border_color;
    cfg->border_radius = (uint8_t)pb->border_radius;
    cfg->padding = (uint8_t)pb->padding;
    cfg->text_color = 0xffffffu;
    cfg->flag_10 = 1u;
    (void)audio_settings_copy_text(cfg->content, pb->content, 0x7ffu);
    cfg->content[0x7ff] = '\0';
}

void evenhub_image_config_from_pb_495f6a(const evenhub_pb_image_t *pb, evenhub_image_config_t *cfg)
{
    if (pb == NULL || cfg == NULL)
        return;
    cfg->x = (int16_t)pb->x;
    cfg->y = (int16_t)pb->y;
    cfg->width = (int16_t)pb->width;
    cfg->height = (int16_t)pb->height;
    cfg->flag_08 = 0u;
    cfg->format = 0xfu;
    cfg->flag_10 = 0u;
    cfg->value_14 = 0u;
    cfg->flag_18 = 1u;
}

/* Centered "Bluetooth disconnected" label shown on the system timeout page. */
void evenhub_ui_create_timeout_exit_page_496430(void *parent)
{
    void *label;

    EH_LOG(4, tmo_fn, 0x5b9, 0x10000000u, tmo_msg, tmo_msg_s);
    label = audio_uart_page_499416(parent);
    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_43f6ac(label, LV_ALIGN_CENTER);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(tmo_text_key,
                                                          audio_uart_page_460084(tmo_text_key)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
}

/* Handles every message the phone sends to a running EvenHub page.
 * Explicit results: -1 bad args / decode / rebuild failure / unknown cmd, 0 rebuild done or
 * ignored during shutdown. Other paths leave r0 as the last callee's result in stock (no
 * return statement); they return 0 here. */
int32_t evenhub_ui_reflash_event_handler_496544(evenhub_manager_t *mgr, const void *data,
                                                int16_t len)
{
    evenhub_msg_t *msg = &g2_evenhub_rx_msg;
    evenhub_pb_istream_t stream;
    evenhub_container_node_t *node;
    evenhub_exit_record_t record;
    uint8_t cmd;
    uint16_t which;

    EH_LOG(4, rf_fn, 0x5c6, 0x10000000u, rf_enter, rf_enter_s);
    if (mgr == NULL) {
        EH_LOG(1, rf_fn, 0x5ca, 0x4000000u, pc_null, pc_null_s);
        return -1;
    }
    if (data == NULL || len == 0) {
        EH_LOG(1, rf_fn, 0x5cf, 0x4000000u, pc_nodata, pc_nodata_s);
        return -1;
    }
    audio_uart_buffer_zero(msg, EVENHUB_MSG_SIZE, 0u);
    stream = audio_uart_pb_stream_init(data, (uint32_t)len);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_evenhub_pb_msg_fields_77754c, msg) == 0u) {
        EH_LOG(1, rf_fn, 0x5d7, 0x4400000u, pc_decode, pc_decode_s,
               (stream.errmsg != NULL) ? stream.errmsg : pc_none);
        return -1;
    }

    cmd = msg->cmd;
    which = msg->which;
    switch (cmd) {
    case EVENHUB_CMD_PRIVATE_EVENT:
        if (which != EVENHUB_WHICH_PRIVATE_EVENT)
            break;
        EH_LOG(3, rf_fn, 0x5e2, 0xc000000u, rf_private, rf_private_s);
        node = evenhub_container_list_find_by_id_493fa8(mgr, msg->value);
        EH_LOG(3, rf_fn, 0x5e4, 0xc400000u, rf_found, rf_found_s, msg->value);
        if (node == NULL) {
            EH_LOG(1, rf_fn, 0x64d, 0x4400000u, rf_missing, rf_missing_s, msg->value);
            break;
        }
        if (node->type == EVENHUB_CONTAINER_LIST) {
            uint8_t event = 0xffu;

            if (EVENHUB_MSG_EVENT_CODE(msg) == EVENHUB_EVENT_CLICK)
                event = 2u;
            else if (EVENHUB_MSG_EVENT_CODE(msg) == EVENHUB_EVENT_SCROLL_UP)
                event = 0u;
            else if (EVENHUB_MSG_EVENT_CODE(msg) == EVENHUB_EVENT_SCROLL_DOWN)
                event = 1u;
            (void)common_list_container_inject_event_4de354(node->ui, event);
        } else if (node->type == EVENHUB_CONTAINER_TEXT) {
            uint8_t event = 0xffu;

            if (EVENHUB_MSG_EVENT_CODE(msg) == EVENHUB_EVENT_SCROLL_UP)
                event = 0u;
            else if (EVENHUB_MSG_EVENT_CODE(msg) == EVENHUB_EVENT_SCROLL_DOWN)
                event = 1u;
            (void)common_text_container_inject_event_4e033c(node->ui, event,
                                                            EVENHUB_MSG_EVENT_DATA(msg) >> 16,
                                                            EVENHUB_MSG_EVENT_DATA(msg) & 0xffffu);
        } else if (node->type == EVENHUB_CONTAINER_IMAGE) {
            /* Image refresh: optional RLE/LZ4 decode into a TLSF buffer sized by the
             * container (+0x44), then hand the pixels to the image container. */
            uint8_t *image = (uint8_t *)node->ui;
            const void *pixels;
            uint32_t length;
            void *decoded;
            int32_t ret;

            EH_LOG(3, rf_fn, 0x609, 0xc000000u, rf_image, rf_image_s);
            if (EVENHUB_MSG_EVENT_CODE(msg) != EVENHUB_EVENT_IMAGE_REFRESH) {
                EH_LOG(1, rf_fn, 0x647, 0x4400000u, rf_bad_event, rf_bad_event_s,
                       EVENHUB_MSG_EVENT_CODE(msg));
                break;
            }
            pixels = *(const void *const *)(image + 0x0c);
            length = *(const uint32_t *)(image + 0x20);
            decoded = NULL;
            if (*(const uint32_t *)(image + 0x18) == EVENHUB_COMPRESS_RLE ||
                *(const uint32_t *)(image + 0x18) == EVENHUB_COMPRESS_LZ4) {
                decoded = file_heap_allocate(*(const uint32_t *)(image + 0x44));
                if (decoded == NULL) {
                    EH_LOG(1, rf_fn, 0x618, 0x4400000u, rf_alloc, rf_alloc_s,
                           *(const uint32_t *)(image + 0x44));
                    break;
                }
                if (*(const uint32_t *)(image + 0x18) == EVENHUB_COMPRESS_LZ4)
                    length = evenhub_lz4_decompress_4e0c0c(*(const void *const *)(image + 0x0c),
                                                           *(const uint32_t *)(image + 0x20),
                                                           decoded,
                                                           *(const uint32_t *)(image + 0x44));
                else
                    length = evenhub_rle_decompress_4e0c34(*(const void *const *)(image + 0x0c),
                                                           *(const uint32_t *)(image + 0x20),
                                                           decoded,
                                                           *(const uint32_t *)(image + 0x44));
                if (length == 0u) {
                    EH_LOG(1, rf_fn, 0x62d, 0x4800000u, rf_unz_fail, rf_unz_fail_s,
                           *(const uint32_t *)(image + 0x18), *(const uint32_t *)(image + 0x20));
                    file_heap_free(decoded);
                    break;
                }
                EH_LOG(3, rf_fn, 0x632, 0xcc00000u, rf_unz_ok, rf_unz_ok_s,
                       *(const uint32_t *)(image + 0x18), *(const uint32_t *)(image + 0x20),
                       length);
                pixels = decoded;
            } else if (*(const uint32_t *)(image + 0x18) != EVENHUB_COMPRESS_NONE) {
                EH_LOG(2, rf_fn, 0x637, 0x8400000u, rf_unz_mode, rf_unz_mode_s,
                       *(const uint32_t *)(image + 0x18));
            }
            ret = common_image_container_set_data_4dc5ae(image, pixels, length);
            if (ret == 0)
                EH_LOG(3, rf_fn, 0x63c, 0xc000000u, rf_img_ok, rf_img_ok_s);
            else
                EH_LOG(1, rf_fn, 0x63e, 0x4400000u, rf_img_fail, rf_img_fail_s, ret);
            if (decoded != NULL)
                file_heap_free(decoded);
        }
        break;

    case EVENHUB_CMD_REBUILD:
        if (mgr->timeout_page == 1u) {
            EH_LOG(4, rf_fn, 0x655, 0x10000000u, rf_shutdown, rf_shutdown_s);
            return 0;
        }
        evenhub_unbind_event_container_494484(mgr);
        evenhub_container_list_destroy_493d02(mgr);
        if (evenhub_ui_page_rebuild_4955b4(data, len, mgr) != 0) {
            EH_LOG(1, rf_fn, 0x65c, 0x4000000u, rf_rebuild_fail, rf_rebuild_fail_s);
            if (audio_uart_service_mode() == EVENHUB_ROLE_MASTER) {
                EH_LOG(1, rf_fn, 0x65e, 0x4000000u, rf_master, rf_master_s);
                (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 6u, 0, 0);
                audio_system_alert_close_464c36(EVENHUB_APP_ID, 0u, 0u, 0u);
            } else {
                uint8_t abnormal[5];

                EH_LOG(1, rf_fn, 0x663, 0x4000000u, rf_slave, rf_slave_s);
                audio_uart_buffer_zero(abnormal, sizeof(abnormal), 0u);
                abnormal[0] = 0u;
                (void)audio_uart_handshake_send(EVENHUB_APP_ID, abnormal, 1u, 0u, 5u);
            }
            return -1;
        }
        return 0;

    case EVENHUB_CMD_TIMEOUT_PAGE:
        if ((uint8_t)msg->value == 0u) {
            EH_LOG(4, rf_fn, 0x671, 0x10000000u, rf_tmo_enter, rf_tmo_enter_s);
            evenhub_unbind_event_container_494484(mgr);
            evenhub_container_list_destroy_493d02(mgr);
            audio_uart_page_44d878(mgr->parent);
            evenhub_ui_create_timeout_exit_page_496430(mgr->parent);
            evenhub_main_timeout_page_set_4e0cc4();
            mgr->timeout_page = 1u;
        } else if ((uint8_t)msg->value == 1u) {
            EH_LOG(4, rf_fn, 0x679, 0x10000000u, rf_tmo_exit, rf_tmo_exit_s);
            Common_Fadeout_Anim_Start_4641b6(mgr->parent, EVENHUB_APP_ID);
            evenhub_main_exit_pending_set_4e0ca0();
        }
        break;

    case EVENHUB_CMD_TEXT_UPGRADE:
        EH_LOG(4, rf_fn, 0x681, 0x10000000u, rf_text, rf_text_s);
        if (which != EVENHUB_WHICH_TEXT_UPGRADE) {
            EH_LOG(1, rf_fn, 0x693, 0x4400000u, rf_which, rf_which_s, which);
            (void)evenhub_send_reply_4d9c86(6u, msg->seq, 10u, 9u);
            break;
        }
        EH_LOG(4, rf_fn, 0x683, 0x10000000u, rf_text, rf_text_s);
        node = evenhub_container_list_find_by_id_493fa8(mgr, msg->value);
        if (node == NULL) {
            EH_LOG(1, rf_fn, 0x68e, 0x4400000u, rf_text_missing, rf_text_missing_s, msg->value);
            (void)evenhub_send_reply_4d9c86(6u, msg->seq, 10u, 9u);
            break;
        }
        {
            uint8_t *text = (uint8_t *)node->ui;

            (void)audio_settings_copy_text(text + 0x20, EVENHUB_MSG_TEXT(msg), 0x7ffu);
            text[0x81f] = 0u;
            EH_LOG(4, rf_fn, 0x689, 0x10000000u, rf_text_ok, rf_text_ok_s);
            (void)common_text_container_inject_event_4e033c(text, 2u, 0u, 0u);
            (void)evenhub_send_reply_4d9c86(6u, msg->seq, 10u, 8u);
        }
        break;

    case EVENHUB_CMD_SHUTDOWN:
        if (which != EVENHUB_WHICH_SHUTDOWN) {
            EH_LOG(1, rf_fn, 0x6b2, 0x4400000u, rf_which, rf_which_s, which);
            (void)evenhub_send_reply_4d9c86(10u, msg->seq, 0xcu, 0xbu);
            break;
        }
        EH_LOG(4, rf_fn, 0x69c, 0x10000000u, rf_shut, rf_shut_s);
        (void)evenhub_send_reply_4d9c86(10u, msg->seq, 0xcu, 10u);
        if (msg->value == 0u) {
            evenhub_main_shutdown_state_set_4e0cb2(1u);
            EH_LOG(4, rf_fn, 0x6a3, 0x10000000u, rf_exit_now, rf_exit_now_s);
            if (mgr->parent == NULL)
                break;
            Common_Fadeout_Anim_Start_4641b6(mgr->parent, EVENHUB_APP_ID);
            evenhub_main_exit_pending_set_4e0ca0();
            record = g2_evenhub_exit_record_init;
            record.widget = evenhub_main_widget_id_4935fe();
            audio_uart_ring_wear_persist_48eb32(EVENHUB_EXIT_RECORD_KEY, 2u, &record);
        } else {
            evenhub_main_shutdown_state_set_4e0cb2(1u);
            if (audio_uart_device_role_get() == EVENHUB_ROLE_MASTER) {
                EH_LOG(4, rf_fn, 0x6ad, 0x10000000u, rf_popup, rf_popup_s);
                system_close_page_factory_0046ae9c(1u, EVENHUB_APP_ID);
            }
        }
        break;

    case EVENHUB_CMD_AUDIO_CTRL_ACK:
        if (which == EVENHUB_WHICH_AUDIO_CTRL_ACK) {
            evenhub_main_audio_ack_clear_4e0cba();
            (void)evenhub_send_audio_ctrl_ack_4d9bfe(msg->seq, EVENHUB_CMD_AUDIO_CTRL_ACK,
                                                     msg->value);
        }
        break;

    case EVENHUB_CMD_AUDIO_CTRL:
        if (which == EVENHUB_WHICH_AUDIO_CTRL) {
            EH_LOG(4, rf_fn, 0x6c3, 0x10400000u, rf_audio, rf_audio_s, msg->value);
            (void)evenhub_send_audio_ctrl_reply_4da56e(msg->seq,
                                                       evenhub_audio_acquire_set_4e1406(msg->value));
        }
        break;

    default:
        EH_LOG(1, rf_fn, 0x6cd, 0x4400000u, rf_cmd, rf_cmd_s, cmd);
        return -1;
    }
    return 0;
}
