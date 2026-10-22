/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\onboarding.c
 * Native 0x467ff0..0x46908b (onboarding_check_start_disp 0x46805a is in
 * app/onboarding-check/onboarding_check_start_46805a.c); literal pools
 * 0x468a30..0x468a3f, 0x468c24..0x468c67, 0x468f04..0x468f23, 0x46908c..0x46916b.
 *
 * Page controller of the onboarding app (application id 0x10): UI registry
 * data/UI handlers, BLE disconnect/reconnect bookkeeping on the master, and
 * the darken/restore colour pass used while another app covers the page.
 * Style property ids (LVGL 9.3 fork): 49 LV_STYLE_BORDER_COLOR, 68 IMAGE_OPA,
 * 69 IMAGE_RECOLOR, 70 IMAGE_RECOLOR_OPA, 88 TEXT_COLOR. The stock helpers
 * named *_bg_color / *_image_recolor actually read properties 49 and 88. */
#include <stdint.h>
#include <stddef.h>
#include "g2_kvdb.h"

#define ONBOARDING_APP_ID 0x10u
#define ONBOARDING_LAST_PROCESS 4u      /* process_id that completes onboarding */
#define ONBOARDING_FOREGROUND_SELF 0x21u /* foreground id that keeps colours */
#define DIM_GREY 0x333333u

/* Onboarding process record (RAM 0x200f4800), shared with onboarding_data_manager.c. */
typedef struct {
    uint8_t process_id; /* +0 */
    uint8_t substep;    /* +1 */
    uint8_t status;     /* +2 2 after APP_PbRxOnboardingFrameDataProcess stored a process */
} g2_onboarding_process_t;

/* State saved by the BLE status callback across a disconnect (RAM 0x200f47c4). */
typedef struct {
    uint8_t process_id; /* +0 */
    uint8_t substep;    /* +1 */
    uint8_t saved;      /* +2 */
} g2_onboarding_ble_saved_t;

/* lv_image_header_t word 0: magic [7:0], cf [15:8], flags [31:16]. */
typedef struct {
    uint32_t word0;
    uint32_t size;
    uint32_t stride;
} g2_lv_image_header_t;
_Static_assert(sizeof(g2_lv_image_header_t) == 12, "LVGL 9 image header");

enum {
    LV_CF_L8 = 6u, LV_CF_I1 = 7u, LV_CF_I2 = 8u, LV_CF_I4 = 9u, LV_CF_I8 = 10u,
};

extern g2_onboarding_process_t g2_onboarding_process;        /* RAM 0x200f4800 (pool 0x468c24) */
extern g2_onboarding_ble_saved_t g2_onboarding_ble_saved;    /* RAM 0x200f47c4 (pool 0x469100) */
extern void *g2_onboarding_mutex;                            /* RAM 0x20074830 (pool 0x468c28) */
extern void *g2_onboarding_root_obj;                         /* RAM 0x20074834 (pool 0x469118) */
extern uint32_t g2_onboarding_darkened;                      /* RAM 0x20074838 (pool 0x469124) */
extern uint8_t audio_uart_registry_context_20002e34[];       /* RAM 0x20002e34, +4 page object */
extern const uint8_t audio_uart_image_class_756108[];        /* lv_image_class, ROM 0x756108 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *osMutexNew(const void *attr);                                  /* 0x44971c */
extern uint8_t audio_uart_device_role_get(void);                            /* 0x45a568 */
extern uint32_t audio_log_wake_allowed(void);                               /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);       /* 0x4434d0 */
extern uint32_t audio_onboarding_flag_get_4a7832(void);                     /* kvdbOnboardingConfigGet */
extern uint32_t audio_uart_lv_style_property_44bdea(void *object, uint32_t selector, uint32_t property); /* lv_obj_get_style_prop */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                       /* lv_color_hex */
extern uint32_t audio_uart_page_441068(uint32_t red, uint32_t green, uint32_t blue); /* lv_color_make */
extern uint32_t audio_uart_page_rgb_equal_44102e(uint32_t first, uint32_t second); /* lv_color_eq */
extern void audio_uart_page_4412ec(void *object, uint32_t color, uint32_t selector); /* border_color */
extern void audio_uart_page_44140e(void *object, uint32_t color, uint32_t selector); /* text_color */
extern void audio_uart_page_4413ce(void *object, uint32_t opa, uint32_t selector);   /* image_opa */
extern void lv_obj_set_style_image_recolor_4413de(void *object, uint32_t color, uint32_t selector);
extern void lv_obj_set_style_image_recolor_opa_4413fe(void *object, uint32_t opa, uint32_t selector);
extern uint32_t lv_obj_check_type_43e2bc(const void *object, const void *class_p);
extern const void *lv_image_get_src_498b50(void *image);
extern uint32_t audio_uart_lv_image_header_488f6a(const void *source, void *header); /* lv_image_decoder_get_info */
extern uint32_t audio_uart_lv_child_count_44ddea(void *object);
extern void *audio_uart_lv_child_get_44dce2(void *object, int32_t index);
extern int32_t APP_PbRxOnboardingFrameDataProcess(const uint8_t *data, uint16_t length); /* 0x4a78d0 */
extern void onboarding_flag_update(uint32_t flag);                          /* 0x47e470 */
extern void RPC_OnboardingFlagReplyToPeer(uint8_t flag);                    /* 0x47e51c */
extern void RPC_OnboardingProcessSyncToPeer(void);                          /* 0x47e58e */
extern void audio_wear_child_46805a(uint32_t unused);                       /* onboarding_check_start_disp */
extern void audio_uart_master_display_start(uint32_t app, const void *payload,
                                            uint16_t length, uint32_t extra); /* 0x464b2e */
extern void audio_uart_master_display_refresh(uint32_t app, const void *payload,
                                              uint16_t length, uint32_t extra); /* 0x464bb2 */
extern void audio_uart_master_display_stop(uint32_t app, const void *payload,
                                           uint16_t length, uint32_t extra); /* 0x464c36 */
extern uint32_t audio_uart_handshake_send(uint32_t app, const void *bytes, uint32_t length,
                                          uint32_t id, uint32_t event);     /* 0x465480 */
extern uint32_t audio_ble_status_register_callback(void (*callback)(uint32_t, const void *)); /* CB_BLE_STATUS_RegisterCallback */
extern void audio_ble_status_unregister_callback(void (*callback)(uint32_t, const void *)); /* CB_BLE_STATUS_UnregisterCallback */
extern void ui_onboarding_main_sub_004A8E6C(uint32_t event, void *data);
extern uint32_t ui_onboarding_main_sub_004A99D0(uint32_t a, uint32_t b);
extern void ui_onboarding_main_sub_004A9C0C(void);
extern void ui_onboarding_main_create_4aba58(void *display);  /* creates g2_onboarding_root_obj */
extern void ui_onboarding_main_destroy_4abba4(void);

static const char module_tag[] = "onboarding"; /* ROM 0x78b630 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding.c"; /* ROM 0x704390 */
static const char darken_fn[] = "onboarding_darken_widget_colors_recursive"; /* ROM 0x740ad0 */
static const char resume_fn[] = "onboarding_resume_widget_colors_recursive"; /* ROM 0x740b54 */
static const char data_fn[] = "Onboarding_common_data_handler";             /* ROM 0x762a10 */
static const char ble_fn[] = "onboarding_ble_status_callback";              /* ROM 0x762a50 */
static const char page_fn[] = "onboarding_page_event_handler";              /* ROM 0x762a70 */
static const char ui_fn[] = "Onboarding_ui_event_handler";                  /* ROM 0x76e8d8 */
static const char indexed_dark[] = "Applied recolor to indexed image (cf=%d)"; /* ROM 0x740afc */
static const char indexed_dark_short[] = "[onboarding]Applied recolor to indexed image (cf=%d)"; /* ROM 0x720b40 */
static const char l8_dark[] = "Applied opacity to L8 image (cf=%d)"; /* ROM 0x757278 */
static const char l8_dark_short[] = "[onboarding]Applied opacity to L8 image (cf=%d)"; /* ROM 0x736044 */
static const char no_info[] = "Failed to get image info, skipping recolor"; /* ROM 0x740b28 */
static const char no_info_short[] = "[onboarding]Failed to get image info, skipping recolor"; /* ROM 0x720b78 */
static const char indexed_resume[] = "Applied white recolor to indexed image (cf=%d)"; /* ROM 0x736074 */
static const char indexed_resume_short[] = "[onboarding]Applied white recolor to indexed image (cf=%d)"; /* ROM 0x716e34 */
static const char l8_resume[] = "Restored opacity for L8 image (cf=%d)"; /* ROM 0x74bc0c */
static const char l8_resume_short[] = "[onboarding]Restored opacity for L8 image (cf=%d)"; /* ROM 0x72b640 */
static const char recv_len[] = "Onboarding recv data len = %d"; /* ROM 0x762a30 */
static const char recv_len_short[] = "[onboarding]Onboarding recv data len = %d"; /* ROM 0x740b80 */
static const char start_up[] = "start up onboarding, process_id = %d"; /* ROM 0x74bc34 */
static const char start_up_short[] = "[onboarding]start up onboarding, process_id = %d"; /* ROM 0x72b674 */
static const char pb_failed[] = "APP_PbRxOnboardingFrameDataProcess failed"; /* ROM 0x740bac */
static const char pb_failed_short[] = "[onboarding]APP_PbRxOnboardingFrameDataProcess failed"; /* ROM 0x720bb0 */
static const char bad_len[] = "Onboarding: invalid peer message length"; /* ROM 0x74bc5c */
static const char bad_len_short[] = "[onboarding]Onboarding: invalid peer message length"; /* ROM 0x72b6a8 */
static const char peer_process[] = "Onboarding: received process_id=%d, substep=%d"; /* ROM 0x7360a4 */
static const char peer_process_short[] = "[onboarding]Onboarding: received process_id=%d, substep=%d"; /* ROM 0x716e70 */
static const char flags_fmt[] = "Onboarding: peer_flag=%d, local_flag=%d, final_flag=%d"; /* ROM 0x720be8 */
static const char flags_short[] = "[onboarding]Onboarding: peer_flag=%d, local_flag=%d, final_flag=%d"; /* ROM 0x7043d4 */
static const char flag_updated[] = "Onboarding: flag updated from %d to %d"; /* ROM 0x74bc84 */
static const char flag_updated_short[] = "[onboarding]Onboarding: flag updated from %d to %d"; /* ROM 0x72b6dc */
static const char peer_disc[] = "Onboarding: received BLE disconnect event"; /* ROM 0x740bd8 */
static const char peer_disc_short[] = "[onboarding]Onboarding: received BLE disconnect event"; /* ROM 0x720c20 */
static const char peer_reconn[] = "Onboarding: received BLE reconnect event"; /* ROM 0x740c04 */
static const char peer_reconn_short[] = "[onboarding]Onboarding: received BLE reconnect event"; /* ROM 0x720c58 */
static const char unknown_cmd[] = "Onboarding: unknown peer sync cmd=%d"; /* ROM 0x74bcac */
static const char unknown_cmd_short[] = "[onboarding]Onboarding: unknown peer sync cmd=%d"; /* ROM 0x72b710 */
static const char ble_invalid[] = "Onboarding: invalid ble status data"; /* ROM 0x75729c */
static const char ble_invalid_short[] = "[onboarding]Onboarding: invalid ble status data"; /* ROM 0x7360d4 */
static const char ble_changed[] = "Onboarding: ble status changed to %d"; /* ROM 0x74bcd4 */
static const char ble_changed_short[] = "[onboarding]Onboarding: ble status changed to %d"; /* ROM 0x72b744 */
static const char ble_idle[] = "Onboarding: app not running, ignore ble status change"; /* ROM 0x720c90 */
static const char ble_idle_short[] = "[onboarding]Onboarding: app not running, ignore ble status change"; /* ROM 0x704418 */
static const char ble_saving[] =
    "Onboarding: BLE disconnected, saving current state (process_id=%d, substep=%d)"; /* ROM 0x6eeb98 */
static const char ble_saving_short[] =
    "[onboarding]Onboarding: BLE disconnected, saving current state (process_id=%d, substep=%d)"; /* ROM 0x6e1098 */
static const char ble_restoring[] =
    "Onboarding: BLE reconnected, restoring state (process_id=%d, substep=%d)"; /* ROM 0x6f4e54 */
static const char ble_restoring_short[] =
    "[onboarding]Onboarding: BLE reconnected, restoring state (process_id=%d, substep=%d)"; /* ROM 0x6e4698 */
static const char foreground[] = "foregroundID = %d"; /* ROM 0x781548 */
static const char foreground_short[] = "[onboarding]foregroundID = %d"; /* ROM 0x762a90 */
static const char darken_msg[] = "onboarding_darken_widget_colors_recursive"; /* ROM 0x740c30 */
static const char darken_msg_short[] = "[onboarding]onboarding_darken_widget_colors_recursive"; /* ROM 0x720cc8 */
static const char resume_msg[] = "onboarding_resume_widget_colors_recursive"; /* ROM 0x740c5c */
static const char resume_msg_short[] = "[onboarding]onboarding_resume_widget_colors_recursive"; /* ROM 0x720d00 */
static const char stop_again[] = "Onboarding: request display stop again"; /* ROM 0x74bcfc */
static const char stop_again_short[] = "[onboarding]Onboarding: request display stop again"; /* ROM 0x72b778 */
static const char imu_reflash[] = "IMU Reflash Event."; /* ROM 0x78155c */
static const char imu_reflash_short[] = "[onboarding]IMU Reflash Event."; /* ROM 0x762ab0 */
static const char ui_init[] = "Onboarding_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x736104 */
static const char ui_init_short[] = "[onboarding]Onboarding_ui_event_handler UI_EVENT_TYPE_INIT"; /* ROM 0x716eac */
static const char cb_ok[] = "Onboarding: BLE status callback registered successfully"; /* ROM 0x720d38 */
static const char cb_ok_short[] = "[onboarding]Onboarding: BLE status callback registered successfully"; /* ROM 0x70445c */
static const char cb_failed[] = "Onboarding: failed to register BLE status callback"; /* ROM 0x72b7ac */
static const char cb_failed_short[] = "[onboarding]Onboarding: failed to register BLE status callback"; /* ROM 0x70d524 */
static const char ui_exit[] = "Onboarding_ui_event_handler UI_EVENT_TYPE_EXIT"; /* ROM 0x736134 */
static const char ui_exit_short[] = "[onboarding]Onboarding_ui_event_handler UI_EVENT_TYPE_EXIT"; /* ROM 0x716ee8 */

void onboarding_ble_status_callback(uint32_t event, const void *data);

/* Plain message: extended log at `level`, compact record with `mask`. */
static void log_plain(uint8_t level, uint32_t mask, const char *function, uint32_t line,
                      const char *message, const char *short_message)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, function, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(mask, short_message, short_message);
}

static void log_one(uint8_t level, uint32_t mask, const char *function, uint32_t line,
                    const char *message, const char *short_message, uint32_t a)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, function, line, message, a);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(mask, short_message, short_message, a);
}

static void log_two(uint8_t level, uint32_t mask, const char *function, uint32_t line,
                    const char *message, const char *short_message, uint32_t a, uint32_t b)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, function, line, message, a, b);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(mask, short_message, short_message, a, b);
}

uint32_t onboarding_get_style_bg_color(void *object, uint32_t selector)
{
    return audio_uart_lv_style_property_44bdea(object, selector, 0x31u);
}

uint32_t onboarding_get_style_image_recolor(void *object, uint32_t selector)
{
    return audio_uart_lv_style_property_44bdea(object, selector, 0x58u);
}

/* Clears the 8-byte block holding the process record at RAM 0x200f4800. */
void onboarding_saved_color_state_reset(void)
{
    audio_uart_buffer_zero(&g2_onboarding_process, 8u, 0u);
}

void onboarding_process_mutex_init(void)
{
    if (g2_onboarding_mutex == NULL)
        g2_onboarding_mutex = osMutexNew(NULL);
}

/* Onboarding runs when the stored flag requests it or the app is already up. */
uint32_t onboarding_should_run(void)
{
    if ((uint8_t)audio_onboarding_flag_get_4a7832() == 1u)
        return 1u;
    if (audio_log_wake_allowed() == 1u && audio_quicklist_refresh_enabled_4434d0(ONBOARDING_APP_ID) == 1u)
        return 1u;
    return 0u;
}

static uint32_t image_cf(const g2_lv_image_header_t *header)
{
    return (header->word0 >> 8) & 0xffu;
}

static uint32_t is_indexed(uint32_t cf)
{
    return cf == LV_CF_I1 || cf == LV_CF_I2 || cf == LV_CF_I4 || cf == LV_CF_I8;
}

/* Grey out a widget tree: border 0x333333, white text to 0x333333, indexed
 * images recoloured 0x333333 at full opacity, L8 images at opacity 0x20. */
void onboarding_darken_widget_colors_recursive(void *object)
{
    if (object == NULL)
        return;
    (void)onboarding_get_style_bg_color(object, 0u);
    audio_uart_page_4412ec(object, audio_uart_page_44104c(DIM_GREY), 0u);
    uint32_t text = onboarding_get_style_image_recolor(object, 0u);
    if (audio_uart_page_rgb_equal_44102e(text, audio_uart_page_44104c(0xffffffu)) != 0u)
        audio_uart_page_44140e(object, audio_uart_page_44104c(DIM_GREY), 0u);
    if (lv_obj_check_type_43e2bc(object, audio_uart_image_class_756108) != 0u) {
        const void *src = lv_image_get_src_498b50(object);
        if (src != NULL) {
            g2_lv_image_header_t header;
            if (audio_uart_lv_image_header_488f6a(src, &header) == 1u) {
                if (is_indexed(image_cf(&header))) {
                    lv_obj_set_style_image_recolor_4413de(object, audio_uart_page_441068(0x33u, 0x33u, 0x33u), 0u);
                    lv_obj_set_style_image_recolor_opa_4413fe(object, 0xffu, 0u);
                    log_one(4u, 0x10400000u, darken_fn, 0xa9u, indexed_dark, indexed_dark_short, image_cf(&header));
                } else if (image_cf(&header) == LV_CF_L8) {
                    audio_uart_page_4413ce(object, 0x20u, 0u);
                    log_one(4u, 0x10400000u, darken_fn, 0xadu, l8_dark, l8_dark_short, image_cf(&header));
                }
            } else {
                log_plain(2u, 0x08000000u, darken_fn, 0xb2u, no_info, no_info_short);
            }
        }
    }
    uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t i = 0u; i < count; i++)
        onboarding_darken_widget_colors_recursive(audio_uart_lv_child_get_44dce2(object, (int32_t)i));
}

/* Inverse of the darken pass (white border/text/recolor, L8 opacity 0xff). */
void onboarding_resume_widget_colors_recursive(void *object)
{
    if (object == NULL)
        return;
    audio_uart_page_4412ec(object, audio_uart_page_44104c(0xffffffu), 0u);
    uint32_t text = onboarding_get_style_image_recolor(object, 0u);
    if (audio_uart_page_rgb_equal_44102e(text, audio_uart_page_44104c(DIM_GREY)) != 0u)
        audio_uart_page_44140e(object, audio_uart_page_44104c(0xffffffu), 0u);
    if (lv_obj_check_type_43e2bc(object, audio_uart_image_class_756108) != 0u) {
        const void *src = lv_image_get_src_498b50(object);
        if (src != NULL) {
            g2_lv_image_header_t header;
            if (audio_uart_lv_image_header_488f6a(src, &header) == 1u) {
                if (is_indexed(image_cf(&header))) {
                    lv_obj_set_style_image_recolor_4413de(object, audio_uart_page_441068(0xffu, 0xffu, 0xffu), 0u);
                    lv_obj_set_style_image_recolor_opa_4413fe(object, 0xffu, 0u);
                    log_one(4u, 0x10400000u, resume_fn, 0xdcu, indexed_resume, indexed_resume_short, image_cf(&header));
                } else if (image_cf(&header) == LV_CF_L8) {
                    audio_uart_page_4413ce(object, 0xffu, 0u);
                    log_one(4u, 0x10400000u, resume_fn, 0xe0u, l8_resume, l8_resume_short, image_cf(&header));
                }
            } else {
                log_plain(2u, 0x08000000u, resume_fn, 0xe5u, no_info, no_info_short);
            }
        }
    }
    uint32_t count = audio_uart_lv_child_count_44ddea(object);
    for (uint32_t i = 0u; i < count; i++)
        onboarding_resume_widget_colors_recursive(audio_uart_lv_child_get_44dce2(object, (int32_t)i));
}

static uint32_t onboarding_app_running(void)
{
    return audio_log_wake_allowed() == 1u && audio_quicklist_refresh_enabled_4434d0(ONBOARDING_APP_ID) == 1u;
}

/* Peer flag exchange (cmd 0x0d request, 0x0e reply): final flag is set only
 * when both sides report 1. Returns the local flag. */
static uint8_t merge_flags(uint8_t peer, uint8_t level, uint32_t mask, uint32_t line,
                           uint32_t update_line)
{
    volatile uint8_t *local_p = kvdbOnboardingConfigPointer(0u);
    uint8_t local = local_p != NULL ? *local_p : 0u;
    uint8_t final_flag = (peer == 1u && local == 1u) ? 1u : 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, data_fn, line, flags_fmt,
                           (uint32_t)peer, (uint32_t)local, (uint32_t)final_flag);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(mask, flags_short, flags_short,
                                  (uint32_t)peer, (uint32_t)local, (uint32_t)final_flag);
    if (local_p != NULL && *local_p != final_flag) {
        onboarding_flag_update(final_flag);
        log_two(3u, 0x0c800000u, data_fn, update_line, flag_updated, flag_updated_short,
                (uint32_t)*local_p, (uint32_t)final_flag);
    }
    return local;
}

/* UI registry data handler. type 0: protobuf frame from the phone app;
 * type 5: peer sync message from the other arm ([cmd, args...]). */
uint32_t Onboarding_common_data_handler(uint32_t type, const uint8_t *data, uint32_t length)
{
    log_one(4u, 0x10400000u, data_fn, 0xf3u, recv_len, recv_len_short, length);
    onboarding_process_mutex_init();
    uint8_t role = audio_uart_device_role_get();
    if (data == NULL || length == 0u)
        return 0u;
    if (type == 0u) {
        if (APP_PbRxOnboardingFrameDataProcess(data, (uint16_t)length) != 0) {
            log_plain(1u, 0x04000000u, data_fn, 0x116u, pb_failed, pb_failed_short);
            return 0u;
        }
        if (g2_onboarding_process.status != 2u)
            return 0u;
        if (g2_onboarding_process.process_id == ONBOARDING_LAST_PROCESS) {
            onboarding_flag_update(0u);
            if (role == 1u && onboarding_app_running())
                audio_uart_master_display_stop(ONBOARDING_APP_ID, NULL, 0u, 0u);
        } else if (audio_log_wake_allowed() == 0u ||
                   audio_quicklist_refresh_enabled_4434d0(ONBOARDING_APP_ID) != 1u) {
            log_one(3u, 0x0c400000u, data_fn, 0x108u, start_up, start_up_short,
                    g2_onboarding_process.process_id);
            if (role == 1u)
                audio_uart_master_display_start(ONBOARDING_APP_ID, NULL, 0u, 0u);
        } else if (role == 1u && onboarding_app_running()) {
            uint8_t refresh[1] = {0x0au}; /* ROM 0x78f6e5 */
            audio_uart_master_display_refresh(ONBOARDING_APP_ID, refresh, 1u, 0u);
        }
        return 0u;
    }
    if (type != 5u)
        return 0u;
    if (length == 0u) {
        log_plain(2u, 0x08000000u, data_fn, 0x11eu, bad_len, bad_len_short);
        return 0u;
    }
    uint8_t cmd = data[0];
    if (cmd == 0x09u) {
        if (length > 2u) {
            uint8_t process_id = data[1];
            uint8_t substep = data[2];
            log_two(3u, 0x0c800000u, data_fn, 0x129u, peer_process, peer_process_short,
                    process_id, substep);
            g2_onboarding_process.process_id = process_id;
            g2_onboarding_process.substep = substep;
            if (role == 1u) {
                uint8_t refresh[1] = {0x0au}; /* ROM 0x78f6e6 */
                audio_uart_master_display_refresh(ONBOARDING_APP_ID, refresh, 1u, 0u);
            }
        }
    } else if (cmd == 0x0du) {
        if (length > 1u) {
            uint8_t local = merge_flags(data[1], 4u, 0x10c00000u, 0x140u, 0x145u);
            RPC_OnboardingFlagReplyToPeer(local);
            audio_wear_child_46805a(0u);
        }
    } else if (cmd == 0x0eu) {
        if (length > 1u)
            (void)merge_flags(data[1], 3u, 0x0cc00000u, 0x15bu, 0x160u);
    } else if (cmd == 0x0fu) {
        log_plain(3u, 0x0c000000u, data_fn, 0x169u, peer_disc, peer_disc_short);
        if (role == 1u) {
            uint8_t refresh[2] = {0x0au, 0x01u}; /* ROM 0x78f634 */
            audio_uart_master_display_refresh(ONBOARDING_APP_ID, refresh, 2u, 0u);
        }
    } else if (cmd == 0x10u) {
        log_plain(3u, 0x0c000000u, data_fn, 0x176u, peer_reconn, peer_reconn_short);
        if (role == 1u) {
            uint8_t refresh[2] = {0x0au, 0x00u}; /* ROM 0x78f636 */
            audio_uart_master_display_refresh(ONBOARDING_APP_ID, refresh, 2u, 0u);
        }
    } else {
        log_one(2u, 0x08400000u, data_fn, 0x181u, unknown_cmd, unknown_cmd_short, cmd);
    }
    return 0u;
}

/* Master BLE status callback (data[0]: 0 disconnected, 1 connected): saves
 * the process on disconnect and tells the peer (cmd 0x0f); on reconnect it
 * resyncs the saved process to the peer. */
void onboarding_ble_status_callback(uint32_t event, const void *data)
{
    (void)event;
    if (data == NULL) {
        log_plain(1u, 0x04000000u, ble_fn, 0x197u, ble_invalid, ble_invalid_short);
        return;
    }
    uint8_t status = *(const uint8_t *)data;
    log_one(3u, 0x0c400000u, ble_fn, 0x19cu, ble_changed, ble_changed_short, status);
    if (audio_quicklist_refresh_enabled_4434d0(ONBOARDING_APP_ID) != 1u) {
        log_plain(4u, 0x10000000u, ble_fn, 0x1a0u, ble_idle, ble_idle_short);
        return;
    }
    if (status == 0u) {
        log_two(3u, 0x0c800000u, ble_fn, 0x1a9u, ble_saving, ble_saving_short,
                g2_onboarding_process.process_id, g2_onboarding_process.substep);
        g2_onboarding_ble_saved.process_id = g2_onboarding_process.process_id;
        g2_onboarding_ble_saved.substep = g2_onboarding_process.substep;
        g2_onboarding_ble_saved.saved = 1u;
        uint8_t cmd = 0x0fu;
        (void)audio_uart_handshake_send(ONBOARDING_APP_ID, &cmd, 1u, 0u, 5u);
    } else if (status == 1u && g2_onboarding_ble_saved.saved != 0u) {
        log_two(3u, 0x0c800000u, ble_fn, 0x1b8u, ble_restoring, ble_restoring_short,
                g2_onboarding_ble_saved.process_id, g2_onboarding_ble_saved.substep);
        g2_onboarding_ble_saved.saved = 0u;
        RPC_OnboardingProcessSyncToPeer();
    }
}

/* Page event handler: 0x42 foreground change (darken unless the foreground
 * is 0 or 0x21), 0x43 back to onboarding (restore; master re-requests stop
 * once process 4 is reached), input events forwarded to the main page
 * unless this arm is the slave (role 2), 0x40 IMU refresh log. */
uint32_t onboarding_page_event_handler(uint32_t unused0, uint32_t unused1, uint32_t event, void *data)
{
    (void)unused0;
    (void)unused1;
    if (event == 0x42u) {
        uint32_t foreground_id = data != NULL ? *(const uint32_t *)data : 0u;
        log_one(3u, 0x0c400000u, page_fn, 0x1cfu, foreground, foreground_short, foreground_id);
        if (g2_onboarding_root_obj != NULL && foreground_id != 0u &&
            foreground_id != ONBOARDING_FOREGROUND_SELF) {
            log_plain(4u, 0x10000000u, page_fn, 0x1d4u, darken_msg, darken_msg_short);
            onboarding_darken_widget_colors_recursive(g2_onboarding_root_obj);
            g2_onboarding_darkened = 1u;
        }
        return 1u;
    }
    if (event == 0x43u) {
        if (g2_onboarding_root_obj != NULL && g2_onboarding_darkened == 1u) {
            log_plain(4u, 0x10000000u, page_fn, 0x1deu, resume_msg, resume_msg_short);
            onboarding_resume_widget_colors_recursive(g2_onboarding_root_obj);
            g2_onboarding_darkened = 0u;
        }
        if (audio_uart_device_role_get() == 1u &&
            g2_onboarding_process.process_id == ONBOARDING_LAST_PROCESS) {
            log_plain(3u, 0x0c000000u, page_fn, 0x1f2u, stop_again, stop_again_short);
            audio_uart_master_display_stop(ONBOARDING_APP_ID, NULL, 0u, 0u);
        }
        return 1u;
    }
    if (event == 0x0au || event == 0x48u || event == 0x4bu || event == 0x44u ||
        event == 0x45u || event == 0x08u) {
        if (audio_uart_device_role_get() != 2u)
            ui_onboarding_main_sub_004A8E6C(event, data);
        return 1u;
    }
    if (event == 0x49u)
        return 1u;
    if (event == 0x4au) {
        (void)audio_uart_device_role_get();
        return 1u;
    }
    if (event == 0x40u)
        log_plain(4u, 0x10000000u, page_fn, 0x232u, imu_reflash, imu_reflash_short);
    return 1u;
}

/* UI registry handler: 2 init (create page, BLE callback on master),
 * 3 forwarded to the main page, 4 main-page tick, 5 exit. Unknown events
 * return the second argument unchanged (stock register reuse). */
uint32_t Onboarding_ui_event_handler(uint32_t event, uint32_t a, uint32_t b, void *display)
{
    if (event == 2u) {
        log_plain(4u, 0x10000000u, ui_fn, 0x23bu, ui_init, ui_init_short);
        g2_onboarding_darkened = 0u;
        onboarding_process_mutex_init();
        ui_onboarding_main_create_4aba58(display);
        *(void **)(void *)(audio_uart_registry_context_20002e34 + 4u) = g2_onboarding_root_obj;
        if (audio_uart_device_role_get() == 1u) {
            audio_uart_buffer_zero(&g2_onboarding_ble_saved, 3u, 0u);
            if (audio_ble_status_register_callback(onboarding_ble_status_callback) != 0u)
                log_plain(4u, 0x10000000u, ui_fn, 0x245u, cb_ok, cb_ok_short);
            else
                log_plain(1u, 0x04000000u, ui_fn, 0x247u, cb_failed, cb_failed_short);
        }
        return 0u;
    }
    if (event == 3u)
        return ui_onboarding_main_sub_004A99D0(a, b);
    if (event == 4u) {
        ui_onboarding_main_sub_004A9C0C();
        return 0u;
    }
    if (event == 5u) {
        log_plain(3u, 0x0c000000u, ui_fn, 0x252u, ui_exit, ui_exit_short);
        if (audio_uart_device_role_get() == 1u)
            audio_ble_status_unregister_callback(onboarding_ble_status_callback);
        ui_onboarding_main_destroy_4abba4();
        g2_onboarding_darkened = 0u;
        return 0u;
    }
    return a;
}
