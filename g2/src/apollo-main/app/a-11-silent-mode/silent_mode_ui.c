/* Silent-mode page, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\Silent_Mode\silent_mode.c.
 * Native 0x46916c..0x46919e and 0x469388..0x469b30 (minus 0x46949a, already in
 * app/silent-mode), literal pool 0x469b30..0x469bf3.
 *
 * Page registered for application id 0x10a (registry row 26, context RAM 0x20003a5c).
 * UI events: 2 = display startup, 3 = refresh data, 4 = periodic tick, 5 = display exit.
 * LVGL v9 callees are named after their existing g2/src externs; the LVGL v9 API
 * each one corresponds to is given in its comment. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    void *container;  /* +0x00 full-screen child of the root page */
    void *label;      /* +0x04 */
    void *image[4];   /* +0x08..+0x14, only for the "activated" reminder */
    int32_t ticks;    /* +0x18 periodic-tick counter */
} g2_silent_mode_ui_t;
_Static_assert(sizeof(g2_silent_mode_ui_t) == 0x1c, "stock clears 0x1c bytes");

extern g2_silent_mode_ui_t g2_silent_mode_ui;              /* RAM 0x20073ae4 */
extern void *g2_silent_mode_root_page;                     /* RAM 0x200749c0 */
extern uint8_t audio_silent_mode_ui_status;                /* RAM 0x2007501d, need_turn_on */
extern uint8_t audio_silent_mode_change_from_app;          /* RAM 0x2007501e */
extern uint8_t audio_silent_mode_showing_ui_2007501f;      /* RAM 0x2007501f */
extern uint32_t audio_uart_ring_secondary_head_cell;       /* RAM 0x200746e0, font manager current lv_font_t * */
extern uint8_t audio_uart_registry_context_20003a5c;       /* RAM 0x20003a5c, +4 = root page */
extern const uint8_t g2_silent_mode_image_771d58[];        /* ROM 0x771d58 lv_image_dsc_t */
extern const uint8_t g2_silent_mode_image_771d90[];        /* ROM 0x771d90 lv_image_dsc_t */
extern const uint8_t g2_silent_mode_image_771d3c[];        /* ROM 0x771d3c lv_image_dsc_t */
extern const uint8_t g2_silent_mode_image_771d74[];        /* ROM 0x771d74 lv_image_dsc_t */

/* lv_color_t is three bytes; it is returned and passed in a core register. */
extern void *audio_uart_page_43de82(void *parent);                       /* lv_obj_create */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);            /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);     /* lv_obj_set_size */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* lv_obj_set_style_bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t o, uint32_t sel); /* lv_obj_set_style_bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t c, uint32_t sel); /* lv_obj_set_style_text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t f, uint32_t sel); /* lv_obj_set_style_text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t a, uint32_t sel); /* lv_obj_set_style_text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_radius */
extern void *audio_uart_page_498668(void *parent);                       /* lv_image_create */
extern void audio_uart_page_498680(void *img, const void *src);          /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                       /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);       /* lv_label_set_text */
extern uint32_t audio_uart_page_460084(const char *key);                 /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t value); /* 0x43c0e4 memset */
extern void page_fade_in_anim_start_46410a(void *root);
extern void Common_Fadeout_Anim_Start_4641b6(void *root, uint32_t app_id);
extern uint8_t audio_uart_device_role_get(void);                         /* 0x45a568, 1 = master */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t, uint32_t, uint32_t);
extern int32_t audio_uart_master_display_refresh(uint32_t app_id, const void *payload,
                                                 uint16_t length, uint32_t extra); /* 0x464bb2 RequestDisplayReflash */
extern int32_t audio_sync_send_to_both_ext_464f76(uint32_t app_id, const void *bytes, uint32_t length,
                                                  uint32_t id, uint32_t event);
extern uint8_t silent_mode_status_get(void);                            /* 0x46919e */
extern void SilentMode_SetStatus(uint32_t enabled);                     /* 0x4691bc */
extern void notify_silent_mode_to_app(uint32_t enabled);                /* 0x49bf24 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#define SILENT_MODE_APP_ID 0x10au

static const char module_tag[] = "silent_mode"; /* ROM 0x78c128 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\Silent_Mode\\silent_mode.c"; /* ROM 0x6fd394 */
static const char toggle_fn[] = "SilentMode_ToggleByLocalLongPress"; /* ROM 0x75a464 */
static const char ui_fn[] = "silent_mode_ui_event_handler"; /* ROM 0x7656d0 */
static const char showing_fn[] = "get_silent_mode_ui_showing"; /* ROM 0x771d20 */
static const char text_on[] = "ON";   /* ROM 0x469578 */
static const char text_off[] = "OFF"; /* ROM 0x46957c */
static const char current_msg[] = "Current status: %s"; /* ROM 0x783834 */
static const char current_short[] = "[silent_mode]Current status: %s"; /* ROM 0x765690 */
static const char send_fail_msg[] = "Failed to send data to both: ret=%d"; /* ROM 0x75a488 */
static const char send_fail_short[] = "[silent_mode]Failed to send data to both: ret=%d"; /* ROM 0x72dfb0 */
static const char startup_msg[] = "Silent mode display startup, need_turn_on=%d"; /* ROM 0x738b64 */
static const char startup_short[] = "[silent_mode]Silent mode display startup, need_turn_on=%d"; /* ROM 0x718d60 */
static const char off_id[] = "ID_SILENT_MODE_OFF"; /* ROM 0x783848 */
static const char reminder_id[] = "ID_SILENT_MODE_ACTIVATED_REMINDER"; /* ROM 0x75a4ac */
static const char exit_refresh_msg[] = "Silent mode received exit refresh command"; /* ROM 0x743d84 */
static const char exit_refresh_short[] = "[silent_mode]Silent mode received exit refresh command"; /* ROM 0x723578 */
static const char root_null_msg[] = "Root page is NULL, deactivating UI"; /* ROM 0x75a4d0 */
static const char root_null_short[] = "[silent_mode]Root page is NULL, deactivating UI"; /* ROM 0x738b94 */
static const char timeout_msg[] = "Silent mode timeout, sending exit command RequestDisplayReflash"; /* ROM 0x70f4a4 */
static const char timeout_short[] = "[silent_mode]Silent mode timeout, sending exit command RequestDisplayReflash"; /* ROM 0x6efd18 */
static const char exit_fail_msg[] = "Failed to send exit command: ret=%d"; /* ROM 0x75a4f4 */
static const char exit_fail_short[] = "[silent_mode]Failed to send exit command: ret=%d"; /* ROM 0x72dfe4 */
static const char exit_msg[] = "Silent mode display exit"; /* ROM 0x771d04 */
static const char exit_short[] = "[silent_mode]Silent mode display exit"; /* ROM 0x74e95c */
static const char showing_msg[] = "silent mode is showing_ui: %d"; /* ROM 0x7656f0 */
static const char showing_short[] = "[silent_mode]silent mode is showing_ui: %d"; /* ROM 0x743db0 */

/* IAR out-of-line copy of LVGL's static inline lv_obj_set_style_pad_all(). */
void silent_mode_apply_text_style(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Long press on the local temple: ask both sides to flip silent mode. */
void SilentMode_ToggleByLocalLongPress(void)
{
    if (audio_silent_mode_showing_ui_2007501f != 0u)
        return;
    uint8_t current = silent_mode_status_get();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, toggle_fn, 0x8du, current_msg,
                           current != 0u ? text_on : text_off);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, current_short, current_short,
                                  current != 0u ? text_on : text_off);
    uint8_t target = current == 0u ? 1u : 0u;
    int32_t ret = audio_sync_send_to_both_ext_464f76(SILENT_MODE_APP_ID, &target, 1u, 0u, 4u);
    if (ret != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, toggle_fn, 0x96u, send_fail_msg, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, send_fail_short, send_fail_short, ret);
    }
}

void silent_mode_noop_callback(void)
{
}

/* Key filter: every key (0x0a, 0x42..0x45, 0x48 and the rest) is accepted. */
uint32_t silent_mode_refresh_callback(uint32_t page, uint32_t arg, uint32_t key)
{
    (void)page;
    (void)arg;
    switch (key) {
    case 0x42u:
        return 1u;
    case 0x43u:
        return 1u;
    case 0x0au:
    case 0x44u:
    case 0x45u:
    case 0x48u:
        return 1u;
    default:
        return 1u;
    }
}

static void *full_screen_child(void *parent, uint32_t with_background)
{
    void *obj = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(obj, 0x240, 0x120);
    audio_uart_page_43f09a(obj, 0, 0);
    audio_uart_page_43dfa4(obj, 0x10u); /* LV_OBJ_FLAG_SCROLLABLE */
    if (with_background) {
        audio_uart_page_44127e(obj, audio_uart_page_44104c(0x000000u), 0u);
        audio_uart_page_44129e(obj, 0xffu, 0u);
        audio_uart_page_44131c(obj, 0, 0u);
        audio_uart_page_44146a(obj, 0, 0u);
    } else {
        audio_uart_page_44129e(obj, 0u, 0u);
        audio_uart_page_44131c(obj, 0, 0u);
    }
    silent_mode_apply_text_style(obj, 0, 0u);
    return obj;
}

static void *reminder_image(void *parent, int32_t x, int32_t y, const void *src)
{
    void *img = audio_uart_page_498668(parent);
    audio_uart_page_43f09a(img, x, y);
    audio_uart_page_498680(img, src);
    audio_uart_page_43dfa4(img, 0x10u);
    return img;
}

static void display_startup(void *parent)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, ui_fn, 0xd6u, startup_msg,
                           audio_silent_mode_ui_status);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, startup_short, startup_short,
                                  audio_silent_mode_ui_status);
    audio_silent_mode_showing_ui_2007501f = 1u;
    audio_uart_buffer_zero(&g2_silent_mode_ui, sizeof g2_silent_mode_ui, 0u);

    g2_silent_mode_root_page = full_screen_child(parent, 1u);
    g2_silent_mode_ui.container = full_screen_child(g2_silent_mode_root_page, 0u);
    void *label = audio_uart_page_499416(g2_silent_mode_ui.container);
    g2_silent_mode_ui.label = label;
    if (audio_silent_mode_ui_status != 0u) {
        audio_uart_page_43f4c0(label, 0x1e4, 0x5a);
        audio_uart_page_44145a(label, 2u, 0u); /* LV_TEXT_ALIGN_CENTER */
        audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44143e(label, audio_uart_ring_secondary_head_cell, 0u);
        audio_uart_page_44129e(label, 0u, 0u);
        audio_uart_page_44131c(label, 0, 0u);
        audio_uart_page_49942e(label, audio_uart_page_45fffe(reminder_id, audio_uart_page_460084(reminder_id)));
        audio_uart_page_43f6b8(label, 2u, 0, 0x20); /* LV_ALIGN_TOP_MID */
        void *container = g2_silent_mode_ui.container;
        g2_silent_mode_ui.image[2] = reminder_image(container, 0xd4, 0x94, g2_silent_mode_image_771d58);
        g2_silent_mode_ui.image[3] = reminder_image(container, 0x143, 0x94, g2_silent_mode_image_771d90);
        g2_silent_mode_ui.image[0] = reminder_image(container, 0x175, 0xc6, g2_silent_mode_image_771d3c);
        g2_silent_mode_ui.image[1] = reminder_image(container, 0xb4, 0xc6, g2_silent_mode_image_771d74);
    } else {
        audio_uart_page_43f4c0(label, 400, 0x1e);
        audio_uart_page_44145a(label, 2u, 0u);
        audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44143e(label, audio_uart_ring_secondary_head_cell, 0u);
        audio_uart_page_44129e(label, 0u, 0u);
        audio_uart_page_44131c(label, 0, 0u);
        audio_uart_page_49942e(label, audio_uart_page_45fffe(off_id, audio_uart_page_460084(off_id)));
        audio_uart_page_43f6b8(label, 9u, 0, 0); /* LV_ALIGN_CENTER */
    }
    g2_silent_mode_ui.ticks = 0;
    page_fade_in_anim_start_46410a(g2_silent_mode_root_page);
    ((void **)(void *)&audio_uart_registry_context_20003a5c)[1] = g2_silent_mode_root_page;
}

static void refresh_data(const uint8_t *data, uint32_t length)
{
    if (data == NULL || length == 0u || data[0] != 0xffu)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, ui_fn, 0x14fu, exit_refresh_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, exit_refresh_short, exit_refresh_short);
    if (g2_silent_mode_root_page == NULL)
        return;
    Common_Fadeout_Anim_Start_4641b6(g2_silent_mode_root_page, SILENT_MODE_APP_ID);
    audio_silent_mode_showing_ui_2007501f = 0u;
    if (audio_uart_device_role_get() == 1u && audio_silent_mode_ui_status == 0u) {
        notify_silent_mode_to_app(0u);
        (void)audio_system_alert_command_45a8ee(1u, 0u, 0u, 500u);
    }
}

/* About 180 ticks after startup the master asks the page to close itself. */
static void periodic_tick(void)
{
    if (g2_silent_mode_root_page == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, ui_fn, 0x161u, root_null_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08000000u, root_null_short, root_null_short);
        return;
    }
    g2_silent_mode_ui.ticks++;
    if (g2_silent_mode_ui.ticks <= 0xb3)
        return;
    g2_silent_mode_ui.ticks = 0;
    if (audio_uart_device_role_get() != 1u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, ui_fn, 0x16cu, timeout_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, timeout_short, timeout_short);
    uint8_t exit_command = 0xffu;
    int32_t ret = audio_uart_master_display_refresh(SILENT_MODE_APP_ID, &exit_command, 1u, 0u);
    if (ret != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, ui_fn, 0x171u, exit_fail_msg, ret);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04400000u, exit_fail_short, exit_fail_short, ret);
    }
}

static void display_exit(void)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, ui_fn, 0x17au, exit_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, exit_short, exit_short);
    if (audio_silent_mode_ui_status != 0u) {
        SilentMode_SetStatus(1u);
        notify_silent_mode_to_app(1u);
    }
    audio_silent_mode_showing_ui_2007501f = 0u;
    audio_silent_mode_change_from_app = 0u;
    silent_mode_noop_callback();
}

uint32_t silent_mode_ui_event_handler(uint32_t event, const uint8_t *data, uint32_t length, void *parent)
{
    if (event == 2u)
        display_startup(parent);
    else if (event == 3u)
        refresh_data(data, length);
    else if (event == 4u)
        periodic_tick();
    else if (event == 5u)
        display_exit();
    return 0u;
}

uint8_t get_silent_mode_ui_showing(void)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, showing_fn, 0x18bu, showing_msg,
                           audio_silent_mode_showing_ui_2007501f);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, showing_short, showing_short,
                                  audio_silent_mode_showing_ui_2007501f);
    return audio_silent_mode_showing_ui_2007501f;
}
