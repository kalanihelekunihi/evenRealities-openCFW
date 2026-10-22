/* EvenHub loading page, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_loading_Page.c
 * (log tag "evenhub.loading_page", UI registry app id 0xffe). Native 0x492cb4..0x492f8b and
 * 0x492fdc..0x4934fd (literal pool 0x493500..0x4935cb). evenhub_loading_page_common_data_handler
 * 0x492f8c of the same file is not part of this unit.
 *
 * The page shows one centred label while a third-party plugin starts: "starting <name>" when
 * the phone link is up (and asks the phone to start ext_app_id), "Bluetooth disconnected"
 * otherwise. A 1-per-tick countdown (900 ticks while starting, 300 after an error or without
 * BLE) closes the page from the master arm unless another page is in the foreground. */
#include <stdint.h>
#include <stddef.h>

#define EVENHUB_LOADING_APP_ID 0xffeu
#define EVENHUB_LOADING_TIMEOUT_START 900
#define EVENHUB_LOADING_TIMEOUT_SHORT 300
#define DEVICE_ROLE_MASTER 1u

/* Page events (evenhub_loading_page_event_handler). */
#define PAGE_EVENT_INPUT 0x0au
#define PAGE_EVENT_FOREGROUND 0x42u
#define PAGE_EVENT_BACKGROUND_EXIT 0x43u
#define PAGE_EVENT_INPUT_44 0x44u
#define PAGE_EVENT_INPUT_45 0x45u
#define PAGE_EVENT_DOUBLE_CLICK 0x48u
#define PAGE_EVENT_SYSTEM_EXIT_NOTIFY 0x4fu
#define FOREGROUND_NONE 0u
#define FOREGROUND_SELF 0x21u

/* UI registry events (evenhub_loading_page_ui_event_handler). */
#define UI_EVENT_DISPLAY_STARTUP 2u
#define UI_EVENT_DISPLAY_REFLASH 3u
#define UI_EVENT_TICK 4u
#define UI_EVENT_EXIT 5u
#define REFLASH_ID_ERROR 1u

#define LV_ALIGN_CENTER 9u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_LABEL_LONG_WRAP 0u
#define LOADING_LABEL_WIDTH 570

extern void *g2_evenhub_loading_root_obj;           /* RAM 0x20074590 */
extern int32_t g2_evenhub_loading_timeout_cnt;      /* RAM 0x20074594 */
extern uint32_t g2_evenhub_loading_dimmed;          /* RAM 0x20074598 root at 50% opacity */
extern uint32_t g2_evenhub_loading_foreground;      /* RAM 0x2007459c another page in front */
extern void *g2_evenhub_loading_label;              /* RAM 0x200745a0 */
extern uint32_t g2_evenhub_loading_startup_widget_id; /* RAM 0x200745a4 ext_app_id being started */
extern uint32_t audio_uart_ring_primary_head_cell;  /* RAM 0x200746dc: active lv_font_t * */
extern uint8_t audio_uart_registry_context_20000b1c; /* UI registry context: +4 page root object */

extern void audio_uart_page_44120e(void *obj, int32_t value, uint32_t selector); /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t value, uint32_t selector); /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t value, uint32_t selector); /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t value, uint32_t selector); /* style pad_right */
extern void *audio_uart_page_43de82(void *parent);                               /* lv_obj_create */
extern int32_t lv_pct_4515d2(int32_t percent);
extern void audio_uart_page_43f506(void *obj, int32_t width);                    /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);                   /* lv_obj_set_height */
extern void audio_uart_page_43f6ac(void *obj, uint32_t align);                   /* lv_obj_set_align */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                    /* lv_obj_remove_flag */
extern void audio_uart_page_43f66c(void *obj);                                   /* lv_obj_invalidate */
extern void audio_uart_page_44129e(void *obj, uint32_t value, uint32_t selector); /* style bg_opa */
extern void audio_uart_page_44131c(void *obj, uint32_t value, uint32_t selector); /* style setter */
extern void audio_uart_page_44133a(void *obj, uint32_t value, uint32_t selector); /* style setter */
extern void audio_uart_page_441386(void *obj, uint32_t value, uint32_t selector); /* style setter */
extern void audio_uart_page_44146a(void *obj, uint32_t value, uint32_t selector); /* style setter */
extern void audio_uart_page_48ba78(void *obj, uint32_t value);
extern void audio_uart_page_48ba92(void *obj, uint32_t a, uint32_t b, uint32_t c);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                             /* lv_color_hex */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t selector); /* style text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t selector);   /* style text_opa */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t selector);  /* style text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t selector); /* style text_align */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t selector); /* style opa */
extern void *audio_uart_page_499416(void *parent);                               /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);               /* lv_label_set_text */
extern void audio_uart_page_499678(void *label, uint32_t mode);                  /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                         /* i18n key lookup */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);      /* i18n text */
extern int32_t g2_audio_dump_snprintf(char *, uint32_t, const char *, ...);      /* 0x44b728 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t UX_GetSystemBLEStatus(void);                                      /* 0x47d8ce */
extern int32_t evenhub_send_app_startup_4d9e88(uint32_t ext_app_id); /* evenhub_data_parser.c, cmd 0x11 */
extern uint8_t audio_uart_device_role_get(void);                                  /* 0x45a568 */
extern uint32_t audio_uart_service_mode(void);                                    /* 0x45a570 */
extern int32_t audio_system_alert_close_464c36(uint32_t app, uint32_t payload, uint32_t len,
                                               uint32_t context); /* send app exit to UI */
extern void system_close_page_factory_0046ae9c(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);                                                /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);       /* 0x43ce9e */

void evenhub_loading_obj_set_style_pad_all_492cb4(void *obj, int32_t value, uint32_t selector);
uint32_t evenhub_loading_widget_id_492ce6(void);
uint32_t evenhub_loading_page_event_handler_492cee(uint32_t unused0, uint32_t unused1, uint32_t event,
                                                   const uint32_t *data);
uint32_t evenhub_loading_page_ui_event_handler_492fdc(uint32_t event, const uint8_t *data, uint32_t length,
                                                      void *parent);

static const char tag[] = "evenhub.loading_page"; /* ROM 0x777594 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_loading_Page.c"; /* ROM 0x6f3564 */
static const char page_fn[] = "evenhub_loading_page_event_handler"; /* ROM 0x7545e4 */
static const char ui_fn[] = "evenhub_loading_page_ui_event_handler"; /* ROM 0x749f9c */
static const char foreground[] = "foregroundID = %d"; /* ROM 0x77f3ec */
static const char foreground_s[] = "[evenhub.loading_page]foregroundID = %d"; /* ROM 0x749f4c */
static const char dim[] = "set navigation page root obj opacity to 50%%"; /* ROM 0x733f74 */
static const char dim_s[] = "[evenhub.loading_page]set navigation page root obj opacity to 50%%"; /* ROM 0x7028bc */
static const char undim[] = "set navigation page root obj opacity to 100%%"; /* ROM 0x733fa4 */
static const char undim_s[] =
    "[evenhub.loading_page]set navigation page root obj opacity to 100%%"; /* ROM 0x702900 */
static const char double_click[] = "PAGE_EVENT_DOUBLE_CLICK"; /* ROM 0x7775ac */
static const char double_click_s[] = "[evenhub.loading_page]PAGE_EVENT_DOUBLE_CLICK"; /* ROM 0x733fd4 */
static const char close_inject[] = "SystemCloseEventInject"; /* ROM 0x7775c4 */
static const char close_inject_s[] = "[evenhub.loading_page]SystemCloseEventInject"; /* ROM 0x734004 */
static const char exit_notify[] = "PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x749f74 */
static const char exit_notify_s[] = "[evenhub.loading_page]PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event."; /* ROM 0x714f08 */
static const char exit_sent[] = "systemClose application send exit command to UI: ret = %d\n"; /* ROM 0x714f44 */
static const char exit_sent_s[] =
    "[evenhub.loading_page]systemClose application send exit command to UI: ret = %d\n"; /* ROM 0x6e7bc4 */
static const char ui_event[] = "evenhub_loading_page_ui_event_handler eventType = %d"; /* ROM 0x71edf0 */
static const char ui_event_s[] =
    "[evenhub.loading_page]evenhub_loading_page_ui_event_handler eventType = %d"; /* ROM 0x6f35b0 */
static const char startup[] = "DISPLAY_STARTUP eventType = %d"; /* ROM 0x75ff30 */
static const char startup_s[] = "[evenhub.loading_page]DISPLAY_STARTUP eventType = %d"; /* ROM 0x71ee28 */
static const char ext_app[] = "ext_app_id = %d, text = %s"; /* ROM 0x76b7d8 */
static const char ext_app_s[] = "[evenhub.loading_page]ext_app_id = %d, text = %s"; /* ROM 0x72965c */
static const char key_ble_disconnect[] = "ID_GENERAL_BLUETOOTH_DISCONNECT"; /* ROM 0x75ff50 */
static const char key_start_plugins[] = "ID_GENERAL_START_PLUGINS"; /* ROM 0x76b7f4 */
static const char loading_text[] = "temp_buf_loading_string: %s"; /* ROM 0x76b810 */
static const char loading_text_s[] = "[evenhub.loading_page]temp_buf_loading_string: %s"; /* ROM 0x729690 */
static const char widget[] = "evenhub_loading_page_startup_widget_id = %d"; /* ROM 0x73ece8 */
static const char widget_s[] =
    "[evenhub.loading_page]evenhub_loading_page_startup_widget_id = %d"; /* ROM 0x702944 */
static const char reflash_empty[] = "evenhub_loading_page_ui_event_handler DISPLAY_REFLASH len = 0"; /* ROM 0x70b664 */
static const char reflash_empty_s[] =
    "[evenhub.loading_page]evenhub_loading_page_ui_event_handler DISPLAY_REFLASH len = 0"; /* ROM 0x6e7c18 */
static const char reflash_error[] = "error_code = %d, error_string = %s"; /* ROM 0x754608 */
static const char reflash_error_s[] = "[evenhub.loading_page]error_code = %d, error_string = %s"; /* ROM 0x714f80 */
static const char reflash_unknown[] =
    "evenhub_loading_page_ui_event_handler DISPLAY_REFLASH unknown eventID = %d"; /* ROM 0x6f35fc */
static const char reflash_unknown_s[] =
    "[evenhub.loading_page]evenhub_loading_page_ui_event_handler DISPLAY_REFLASH unknown eventID = %d"; /* ROM 0x6da804 */
static const char timeout[] = "evenhub_loading_page_auto_close_timeout_cnt <= 0"; /* ROM 0x7296c4 */
static const char timeout_s[] = "[evenhub.loading_page]evenhub_loading_page_auto_close_timeout_cnt <= 0"; /* ROM 0x6fa3c4 */
static const char ui_unknown[] = "evenhub_loading_page_ui_event_handler unknown eventType = %d"; /* ROM 0x70b6a4 */
static const char ui_unknown_s[] =
    "[evenhub.loading_page]evenhub_loading_page_ui_event_handler unknown eventType = %d"; /* ROM 0x6e7c6c */

#define EL_LOG(level, func, line, cflags, text, short_text, ...)                              \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), tag, file, (func), (line), (text), ##__VA_ARGS__);    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* Out-of-line instance of LVGL's static inline lv_obj_set_style_pad_all in this TU. */
void evenhub_loading_obj_set_style_pad_all_492cb4(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

uint32_t evenhub_loading_widget_id_492ce6(void)
{
    return g2_evenhub_loading_startup_widget_id;
}

/* Page event handler; every event is consumed (returns 1). */
uint32_t evenhub_loading_page_event_handler_492cee(uint32_t unused0, uint32_t unused1, uint32_t event,
                                                   const uint32_t *data)
{
    (void)unused0;
    (void)unused1;
    switch (event) {
    case PAGE_EVENT_FOREGROUND: {
        g2_evenhub_loading_foreground = 1u;
        uint32_t foreground_id = FOREGROUND_NONE;
        if (data != NULL)
            foreground_id = *data;
        EL_LOG(3u, page_fn, 0x58u, 0x0c400000u, foreground, foreground_s, foreground_id);
        if (g2_evenhub_loading_root_obj != NULL && foreground_id != FOREGROUND_NONE &&
            foreground_id != FOREGROUND_SELF) {
            EL_LOG(4u, page_fn, 0x5au, 0x10000000u, dim, dim_s);
            audio_uart_display_audio_reset_441488(g2_evenhub_loading_root_obj, 0x7fu, 0u);
            g2_evenhub_loading_dimmed = 1u;
        }
        return 1u;
    }
    case PAGE_EVENT_BACKGROUND_EXIT:
        g2_evenhub_loading_foreground = 0u;
        if (g2_evenhub_loading_root_obj != NULL && g2_evenhub_loading_dimmed == 1u) {
            EL_LOG(4u, page_fn, 0x63u, 0x10000000u, undim, undim_s);
            audio_uart_display_audio_reset_441488(g2_evenhub_loading_root_obj, 0xffu, 0u);
            g2_evenhub_loading_dimmed = 0u;
        }
        return 1u;
    case PAGE_EVENT_INPUT:
        return 1u;
    case PAGE_EVENT_INPUT_44:
        return 1u;
    case PAGE_EVENT_INPUT_45:
        return 1u;
    case PAGE_EVENT_DOUBLE_CLICK:
        EL_LOG(3u, page_fn, 0x74u, 0x0c000000u, double_click, double_click_s);
        if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
            EL_LOG(3u, page_fn, 0x76u, 0x0c000000u, close_inject, close_inject_s);
            system_close_page_factory_0046ae9c(1u, EVENHUB_LOADING_APP_ID);
        }
        return 1u;
    case PAGE_EVENT_SYSTEM_EXIT_NOTIFY:
        EL_LOG(4u, page_fn, 0x7bu, 0x10000000u, exit_notify, exit_notify_s);
        if ((uint8_t)audio_uart_service_mode() == 1u) {
            int32_t ret = audio_system_alert_close_464c36(EVENHUB_LOADING_APP_ID, 0u, 0u, 0u);
            EL_LOG(4u, page_fn, 0x7fu, 0x10400000u, exit_sent, exit_sent_s, ret);
        }
        return 1u;
    default:
        return 1u;
    }
}

/* UI registry handler (app 0xffe): 2 create, 3 refresh with phone status, 4 tick, 5 exit. */
uint32_t evenhub_loading_page_ui_event_handler_492fdc(uint32_t event, const uint8_t *data, uint32_t length,
                                                      void *parent)
{
    char text[128];

    EL_LOG(4u, ui_fn, 0x9bu, 0x10400000u, ui_event, ui_event_s, event);
    switch (event) {
    case UI_EVENT_DISPLAY_STARTUP: {
        EL_LOG(4u, ui_fn, 0x9eu, 0x10400000u, startup, startup_s, event);
        /* data: +0 unused, +1 ext_app_id (unaligned LE word), +5 NUL-terminated app name. */
        uint32_t ext_app_id = (uint32_t)data[1] | ((uint32_t)data[2] << 8) | ((uint32_t)data[3] << 16) |
                              ((uint32_t)data[4] << 24);
        const char *name = (const char *)data + 5;
        EL_LOG(3u, ui_fn, 0xa3u, 0x0c800000u, ext_app, ext_app_s, ext_app_id, name);
        g2_evenhub_loading_label = NULL;
        g2_evenhub_loading_startup_widget_id = 0u;
        g2_evenhub_loading_dimmed = 0u;
        g2_evenhub_loading_foreground = 0u;
        g2_evenhub_loading_timeout_cnt = EVENHUB_LOADING_TIMEOUT_START;

        g2_evenhub_loading_root_obj = audio_uart_page_43de82(parent);
        audio_uart_page_43f506(g2_evenhub_loading_root_obj, lv_pct_4515d2(100));
        audio_uart_page_43f568(g2_evenhub_loading_root_obj, lv_pct_4515d2(100));
        audio_uart_page_43f6ac(g2_evenhub_loading_root_obj, LV_ALIGN_CENTER);
        audio_uart_page_43dfa4(g2_evenhub_loading_root_obj, LV_OBJ_FLAG_SCROLLABLE);
        audio_uart_page_44129e(g2_evenhub_loading_root_obj, 0u, 0u);
        audio_uart_page_44131c(g2_evenhub_loading_root_obj, 0u, 0u);
        audio_uart_page_44133a(g2_evenhub_loading_root_obj, 0u, 0u);
        audio_uart_page_441386(g2_evenhub_loading_root_obj, 0u, 0u);
        audio_uart_page_44146a(g2_evenhub_loading_root_obj, 0u, 0u);
        evenhub_loading_obj_set_style_pad_all_492cb4(g2_evenhub_loading_root_obj, 0, 0u);
        audio_uart_page_48ba78(g2_evenhub_loading_root_obj, 1u);
        audio_uart_page_48ba92(g2_evenhub_loading_root_obj, 2u, 2u, 2u);
        audio_uart_page_44140e(g2_evenhub_loading_root_obj, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44142e(g2_evenhub_loading_root_obj, 0xffu, 0u);

        if (UX_GetSystemBLEStatus() == 0u) {
            g2_evenhub_loading_label = audio_uart_page_499416(g2_evenhub_loading_root_obj);
            audio_uart_page_43f506(g2_evenhub_loading_label, LV_SIZE_CONTENT);
            audio_uart_page_43f568(g2_evenhub_loading_label, LV_SIZE_CONTENT);
            audio_uart_page_49942e(g2_evenhub_loading_label,
                                   audio_uart_page_45fffe(key_ble_disconnect,
                                                          audio_uart_page_460084(key_ble_disconnect)));
            audio_uart_page_44143e(g2_evenhub_loading_label, audio_uart_ring_primary_head_cell, 0u);
            audio_uart_page_44145a(g2_evenhub_loading_label, LV_TEXT_ALIGN_CENTER, 0u);
            g2_evenhub_loading_timeout_cnt = EVENHUB_LOADING_TIMEOUT_SHORT;
        } else {
            g2_evenhub_loading_label = audio_uart_page_499416(g2_evenhub_loading_root_obj);
            audio_uart_page_43f506(g2_evenhub_loading_label, LOADING_LABEL_WIDTH);
            audio_uart_page_43f568(g2_evenhub_loading_label, LV_SIZE_CONTENT);
            audio_uart_page_499678(g2_evenhub_loading_label, LV_LABEL_LONG_WRAP);
            audio_uart_page_44143e(g2_evenhub_loading_label, audio_uart_ring_primary_head_cell, 0u);
            audio_uart_page_44145a(g2_evenhub_loading_label, LV_TEXT_ALIGN_CENTER, 0u);
            (void)aeabi_memset_43c0e4(text, sizeof(text), 0);
            (void)g2_audio_dump_snprintf(text, sizeof(text),
                                         audio_uart_page_45fffe(key_start_plugins,
                                                                audio_uart_page_460084(key_start_plugins)),
                                         name);
            EL_LOG(4u, ui_fn, 0xceu, 0x10400000u, loading_text, loading_text_s, text);
            audio_uart_page_49942e(g2_evenhub_loading_label, text);
            g2_evenhub_loading_startup_widget_id = ext_app_id;
            (void)evenhub_send_app_startup_4d9e88(ext_app_id);
            g2_evenhub_loading_timeout_cnt = EVENHUB_LOADING_TIMEOUT_START;
        }
        EL_LOG(3u, ui_fn, 0xd5u, 0x0c400000u, widget, widget_s, g2_evenhub_loading_startup_widget_id);
        ((void **)(void *)&audio_uart_registry_context_20000b1c)[1] = g2_evenhub_loading_root_obj;
        return 0u;
    }
    case UI_EVENT_DISPLAY_REFLASH:
        if (length == 0u) {
            EL_LOG(2u, ui_fn, 0xdbu, 0x08000000u, reflash_empty, reflash_empty_s);
            return 0u;
        }
        if (data[0] == REFLASH_ID_ERROR) {
            uint8_t error_code = data[1];
            const char *error_string = (const char *)data + 2;
            EL_LOG(3u, ui_fn, 0xe2u, 0x0c800000u, reflash_error, reflash_error_s, error_code, error_string);
            audio_uart_page_49942e(g2_evenhub_loading_label, error_string);
            audio_uart_page_43f66c(g2_evenhub_loading_root_obj);
            g2_evenhub_loading_timeout_cnt = EVENHUB_LOADING_TIMEOUT_SHORT;
        } else {
            EL_LOG(2u, ui_fn, 0xe7u, 0x08400000u, reflash_unknown, reflash_unknown_s, data[0]);
        }
        return 0u;
    case UI_EVENT_TICK:
        /* The countdown pauses while another page is in the foreground. */
        if (g2_evenhub_loading_foreground == 0u) {
            g2_evenhub_loading_timeout_cnt--;
            if (g2_evenhub_loading_timeout_cnt < 1) {
                EL_LOG(3u, ui_fn, 0xf0u, 0x0c000000u, timeout, timeout_s);
                if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER)
                    (void)audio_system_alert_close_464c36(EVENHUB_LOADING_APP_ID, 0u, 0u, 0u);
            }
        }
        return 0u;
    case UI_EVENT_EXIT:
        g2_evenhub_loading_label = NULL;
        g2_evenhub_loading_dimmed = 0u;
        g2_evenhub_loading_foreground = 0u;
        g2_evenhub_loading_timeout_cnt = 0;
        g2_evenhub_loading_startup_widget_id = 0u;
        return 0u;
    default:
        EL_LOG(2u, ui_fn, 0x101u, 0x08400000u, ui_unknown, ui_unknown_s, event);
        return 0u;
    }
}
