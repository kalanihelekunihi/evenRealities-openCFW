/* System-close confirmation page, stock D:\01_workspace\s200_ap510b_iar_git\app\gui\SystemClose\systemClose.c.
 * Native 0x469bf4..0x469d48 and 0x469e66..0x46b004 (0x469d48 common-data handler is in
 * app/system-close), literal pools 0x46a824, 0x46aab8, 0x46acc4, 0x46ae6c, 0x46b004..0x46b0eb.
 *
 * Application id 0x22 (registry row 30, context RAM 0x20003bf0). The peer (or the local
 * master) opens the page with a 5-byte record {style, app_id[4]} (0x46ae9c); style 1 is the
 * two-item NO/YES confirmation popup. Input codes: 0x0a click, 0x44 scroll up, 0x45 scroll
 * down, 0x48 close, 0x40 IMU refresh. Codes that arrive while the selection animation runs
 * are queued in a 128-byte FIFO (five bytes per event) and replayed by the animation's
 * completed callback.
 *
 * Several TSV names in this range are positional guesses; they are kept for anchoring and
 * the actual behaviour is noted on each function. LVGL v9.3 callees are named after their
 * existing g2/src externs, with the LVGL API in the comment. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t data[0x80];  /* +0x00 */
    uint16_t write;      /* +0x80 */
    uint16_t read;       /* +0x82 */
    uint16_t count;      /* +0x84 */
} g2_system_close_fifo_t;
_Static_assert(offsetof(g2_system_close_fifo_t, count) == 0x84, "fifo count at +0x84");

/* LVGL 9.3 lv_anim_t as laid out on the stack (0x60 bytes, see lv_anim_init 0x4503d6). */
typedef struct {
    void *var;                                  /* +0x00 */
    void (*exec_cb)(void *var, int32_t value);  /* +0x04 */
    void *custom_exec_cb;                       /* +0x08 */
    void *start_cb;                             /* +0x0c */
    void (*completed_cb)(void *anim);           /* +0x10 */
    void *deleted_cb;                           /* +0x14 */
    void *get_value_cb;                         /* +0x18 */
    void *user_data;                            /* +0x1c */
    int32_t (*path_cb)(void *anim);             /* +0x20 */
    int32_t start_value;                        /* +0x24 */
    int32_t current_value;                      /* +0x28 */
    int32_t end_value;                          /* +0x2c */
    int32_t duration;                           /* +0x30 */
    int32_t act_time;                           /* +0x34 */
    uint8_t reserved_38[0x28];
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "lv_anim_t frame");

/* lv_event_t: only the parameter pointer is used. */
typedef struct {
    uint8_t reserved_00[0x10];
    const int32_t *param;  /* +0x10 two coordinates for scroll events */
} g2_system_close_event_t;

enum {
    SC_APP_ID = 0x22u,
    SC_CODE_CLICK = 0x0au,
    SC_CODE_IMU_REFLASH = 0x40u,
    SC_CODE_SCROLL_UP = 0x44u,
    SC_CODE_SCROLL_DOWN = 0x45u,
    SC_CODE_CLOSE = 0x48u,
    SC_CODE_49 = 0x49u,
    SC_CODE_4A = 0x4au,
    SC_CODE_4D = 0x4du,
    SC_CODE_4E = 0x4eu,
};

extern g2_system_close_fifo_t g2_system_close_fifo;   /* RAM 0x20071840 */
extern void *g2_system_close_panel;                   /* RAM 0x200749fc, outer black panel */
extern void *g2_system_close_container;               /* RAM 0x20074a00, bordered box */
extern void *g2_system_close_arrow;                   /* RAM 0x20074a08, selection arrow image */
extern void *g2_system_close_option0;                 /* RAM 0x20074a0c, "NO" */
extern void *g2_system_close_option2;                 /* RAM 0x20074a10, third item (style != 1) */
extern void *g2_system_close_option1;                 /* RAM 0x20074a14, "YES" */
extern int32_t g2_system_close_selected_index;        /* RAM 0x20074a18 */
extern void *g2_system_close_title;                   /* RAM 0x20074a1c */
extern int32_t g2_system_close_item_count;            /* RAM 0x20003bec */
extern volatile uint8_t audio_system_close_selected_20075026; /* RAM 0x20075026, requested style */
extern uint8_t g2_system_close_popup_shown;           /* RAM 0x20075027 */
extern uint8_t g2_system_close_anim_busy;             /* RAM 0x20075028 */
extern uint8_t audio_uart_registry_context_20003bf0;  /* RAM 0x20003bf0, +4 = root page */
extern uint32_t audio_uart_ring_secondary_head_cell;  /* RAM 0x200746e0, font manager current lv_font_t * */
extern const uint8_t g2_system_close_arrow_image[];   /* ROM 0x76a070 lv_image_dsc_t */

/* Layout constants read from ROM by the stock code. */
const int32_t g2_system_close_title_top = 16;      /* ROM 0x78f408 */
const int32_t g2_system_close_side_pad = 20;       /* ROM 0x78f40c */
const int32_t g2_system_close_title_gap = 20;      /* ROM 0x78f410 */
const int32_t g2_system_close_option_gap = 12;     /* ROM 0x78f414 */
const int32_t g2_system_close_panel_height = 0x9c; /* ROM 0x78f418 */
const int32_t g2_system_close_arrow_room = 16;     /* ROM 0x78f41c */

extern void *audio_uart_page_43de82(void *parent);                       /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);            /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);            /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);                /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);                /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);     /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t w);                /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t h);                /* lv_obj_set_height */
extern void audio_uart_page_43f66c(void *obj);                           /* lv_obj_update_layout */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern int32_t audio_uart_lv_obj_x_43fc70(void *obj);                    /* lv_obj_get_x */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                    /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);                /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);               /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                    /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t c, uint32_t sel); /* lv_obj_set_style_bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t o, uint32_t sel); /* lv_obj_set_style_bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t c, uint32_t sel); /* lv_obj_set_style_border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t c, uint32_t sel); /* lv_obj_set_style_text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t f, uint32_t sel); /* lv_obj_set_style_text_font */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);  /* lv_obj_set_style_radius */
extern void audio_uart_page_44d878(void *obj);                           /* lv_obj_clean */
extern void *audio_uart_lv_obj_parent_44dca2(void *obj);                 /* lv_obj_get_parent */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);            /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);             /* lv_obj_set_scroll_dir */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);          /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);  /* lv_anim_start */
extern uint32_t audio_uart_lv_style_unlink_450500(void *var, void *exec_cb); /* lv_anim_delete */
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end); /* lv_anim_set_values */
extern int32_t audio_uart_lv_anim_default_path_450634(void *anim);       /* lv_anim_path_linear */
extern void *audio_uart_page_498668(void *parent);                       /* lv_image_create */
extern void audio_uart_page_498680(void *img, const void *src);          /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                       /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);       /* lv_label_set_text */
extern uint32_t audio_uart_page_460084(const char *key);                 /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t value); /* 0x43c0e4 memset */
extern uint8_t audio_uart_device_role_get(void);                         /* 0x45a568, 1 master, 2 slave */
extern int32_t audio_uart_master_display_refresh(uint32_t app_id, const void *payload,
                                                 uint16_t length, uint32_t extra); /* 0x464bb2 RequestDisplayReflash */
extern void audio_system_alert_close_464c36(uint32_t app_id, uint32_t payload, uint32_t length,
                                            uint32_t context);
extern int32_t audio_uart_input_event_send_464d1c(uint16_t app_id, const void *payload,
                                                  uint32_t length, uint32_t extra);
extern uint32_t async_send_input_event_to_peers_45accc(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void system_close_fifo_reset_00469bf4(void *obj, int32_t value, uint32_t selector);
void system_close_set_style_00469d24(void);
void system_close_update_selection(void);
void system_close_handle_scroll_up(void);
void system_close_handle_scroll_down(void);
void system_close_handle_click(void);
void system_close_process_next_event_0046a4e2(void);
void sc_selection_change_anim_ready_cb(void *anim);

static const char module_tag[] = "system_close"; /* ROM 0x789680 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemClose\\systemClose.c"; /* ROM 0x6fd8a4 */
static const char page_event_fn[] = "system_close_page_event_handler"; /* ROM 0x765a70 */
static const char event_msg[] = "received event: %d"; /* ROM 0x783d48 */
static const char event_short[] = "[system_close]received event: %d"; /* ROM 0x75aa94 */
static const char clicked_msg[] = "LV_EVENT_CLICKED"; /* ROM 0x783d5c */
static const char clicked_short[] = "[system_close]LV_EVENT_CLICKED"; /* ROM 0x765a90 */
static const char scroll_up_event_msg[] = "SCROLLUP_EVENT"; /* ROM 0x789690 */
static const char scroll_up_event_short[] = "[system_close]SCROLLUP_EVENT"; /* ROM 0x765ab0 */
static const char scroll_down_event_msg[] = "SCROLLDOWN_EVENT"; /* ROM 0x783d70 */
static const char scroll_down_event_short[] = "[system_close]SCROLLDOWN_EVENT"; /* ROM 0x765ad0 */
static const char imu_msg[] = "IMU Reflash Event."; /* ROM 0x783d84 */
static const char imu_short[] = "[system_close]IMU Reflash Event."; /* ROM 0x75aab8 */
static const char anim_ready_fn[] = "sc_selection_change_anim_ready_cb"; /* ROM 0x75aadc */
static const char anim_done_msg[] = "Selection change animation complete"; /* ROM 0x75ab00 */
static const char anim_done_short[] = "[system_close]Selection change animation complete"; /* ROM 0x72e3c0 */
static const char pop_msg[] = "Pop event from fifo and execute, code=%d"; /* ROM 0x7443e0 */
static const char pop_short[] = "[system_close]Pop event from fifo and execute, code=%d"; /* ROM 0x723c08 */
static const char update_fn[] = "system_close_update_selection"; /* ROM 0x765af0 */
static const char update_msg[] = "Update selection: index=%d, arrow_x=%d, arrow_y=%d"; /* ROM 0x72e3f4 */
static const char update_short[] = "[system_close]Update selection: index=%d, arrow_x=%d, arrow_y=%d"; /* ROM 0x7065d4 */
static const char up_fn[] = "system_close_handle_scroll_up"; /* ROM 0x765b10 */
static const char up_msg[] = "SCROLLUP: new index=%d"; /* ROM 0x77c28c */
static const char up_short[] = "[system_close]SCROLLUP: new index=%d"; /* ROM 0x74ee0c */
static const char up_last_msg[] = "SCROLLUP: already at last item"; /* ROM 0x765b30 */
static const char up_last_short[] = "[system_close]SCROLLUP: already at last item"; /* ROM 0x738fb4 */
static const char down_fn[] = "system_close_handle_scroll_down"; /* ROM 0x765b50 */
static const char down_msg[] = "SCROLLDOWN: new index=%d"; /* ROM 0x772848 */
static const char down_short[] = "[system_close]SCROLLDOWN: new index=%d"; /* ROM 0x74ee34 */
static const char down_first_msg[] = "SCROLLDOWN: already at first item"; /* ROM 0x75ab24 */
static const char down_first_short[] = "[system_close]SCROLLDOWN: already at first item"; /* ROM 0x738fe4 */
static const char click_fn[] = "system_close_handle_click"; /* ROM 0x772864 */
static const char click_msg[] = "system_close_handle_click: selected_index=%d, item_count=%d"; /* ROM 0x71933c */
static const char click_short[] = "[system_close]system_close_handle_click: selected_index=%d, item_count=%d"; /* ROM 0x6f6744 */
static const char no_msg[] = "User selected: NO (Cancel)"; /* ROM 0x772880 */
static const char no_short[] = "[system_close]User selected: NO (Cancel)"; /* ROM 0x74440c */
static const char yes_msg[] = "User selected: YES (Confirm)"; /* ROM 0x765b70 */
static const char yes_short[] = "[system_close]User selected: YES (Confirm)"; /* ROM 0x744438 */
static const char mini_msg[] = "User selected: MINI (Minimize)"; /* ROM 0x765b90 */
static const char mini_short[] = "[system_close]User selected: MINI (Minimize)"; /* ROM 0x739014 */
static const char options_fn[] = "system_close_create_options"; /* ROM 0x77289c */
static const char options_msg[] = "system_close_create_options: style=%d"; /* ROM 0x74ee5c */
static const char options_short[] = "[system_close]system_close_create_options: style=%d"; /* ROM 0x72e428 */
static const char created_msg[] = "Options created: item_count=%d, selected_index=%d"; /* ROM 0x72e45c */
static const char created_short[] = "[system_close]Options created: item_count=%d, selected_index=%d"; /* ROM 0x70fb24 */
static const char id_no[] = "ID_GENERAL_NO"; /* ROM 0x7896a0 */
static const char id_yes[] = "ID_GENERAL_YES"; /* ROM 0x7896b0 */
static const char id_popup[] = "ID_GENERAL_CONFIRMATION_POPUP"; /* ROM 0x765bb0 */
static const char reflash_fn[] = "system_close_ReflashEventHandler"; /* ROM 0x75ab48 */
static const char reflash_msg[] = "system_close_ReflashEventHandler: style=1"; /* ROM 0x744464 */
static const char reflash_short[] = "[system_close]system_close_ReflashEventHandler: style=1"; /* ROM 0x723c40 */
static const char unknown_msg[] = "system_close_ReflashEventHandler: unknown style=%d"; /* ROM 0x72e490 */
static const char unknown_short[] = "[system_close]system_close_ReflashEventHandler: unknown style=%d"; /* ROM 0x706618 */
static const char ui_fn[] = "system_close_ui_event_handler"; /* ROM 0x765bd0 */
static const char startup_msg[] = "system_close DISPLAY_STARTUP"; /* ROM 0x765bf0 */
static const char startup_short[] = "[system_close]system_close DISPLAY_STARTUP"; /* ROM 0x744490 */
static const char exit_msg[] = "system_close DISPLAY_EXIT"; /* ROM 0x7728b8 */
static const char exit_short[] = "[system_close]system_close DISPLAY_EXIT"; /* ROM 0x74ee84 */

/* Empty exec callback of the selection animation (native 0x46a3d6, not in the inventory). */
void system_close_anim_exec_noop_46a3d6(void *var, int32_t value)
{
    (void)var;
    (void)value;
}

/* 0x469bf4: IAR out-of-line copy of LVGL's static inline lv_obj_set_style_pad_all(). */
void system_close_fifo_reset_00469bf4(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* Returns 0, -3 for bad arguments, -1 when the FIFO lacks room. */
int32_t system_close_fifo_push_00469c26(const uint8_t *src, uint16_t length)
{
    g2_system_close_fifo_t *fifo = &g2_system_close_fifo;
    if (src == NULL || length == 0u)
        return -3;
    if ((uint16_t)(0x80u - fifo->count) < length)
        return -1;
    for (uint16_t i = 0u; i < length; i++) {
        fifo->data[fifo->write] = src[i];
        fifo->write = (uint16_t)((fifo->write + 1u) % 0x80u);
        fifo->count++;
    }
    return 0;
}

uint32_t system_close_fifo_empty_00469c98(void)
{
    return g2_system_close_fifo.count == 0u;
}

/* Returns the number of bytes copied, or -3 for bad arguments. */
int32_t system_close_fifo_pop_00469cac(uint8_t *dst, uint16_t length)
{
    g2_system_close_fifo_t *fifo = &g2_system_close_fifo;
    if (dst == NULL || length == 0u)
        return -3;
    if (fifo->count == 0u)
        return 0;
    if (fifo->count <= length)
        length = fifo->count;
    for (uint16_t i = 0u; i < length; i++) {
        dst[i] = fifo->data[fifo->read];
        fifo->read = (uint16_t)((fifo->read + 1u) % 0x80u);
        fifo->count--;
    }
    return length;
}

/* 0x469d24: actually the FIFO reset. */
void system_close_set_style_00469d24(void)
{
    g2_system_close_fifo_t *fifo = &g2_system_close_fifo;
    fifo->write = 0u;
    fifo->read = 0u;
    fifo->count = 0u;
    audio_uart_buffer_zero(fifo, 0x80u, 0u);
}

/* Forward an input code to the master's page as {0, code, x16, y16}. Returns the
 * RequestDisplayReflash status, 0 while the animation runs, or the code when unhandled. */
int32_t system_close_dispatch_page_action_00469e66(uint32_t code, const g2_system_close_event_t *event)
{
    if (g2_system_close_anim_busy != 0u)
        return 0;
    if (code == SC_CODE_SCROLL_UP) {
        const int32_t *point = event->param;
        uint8_t msg[6] = {0u, SC_CODE_SCROLL_UP, (uint8_t)point[0], (uint8_t)(point[0] >> 8),
                          (uint8_t)point[1], (uint8_t)(point[1] >> 8)};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    if (code == SC_CODE_SCROLL_DOWN) {
        const int32_t *point = event->param;
        uint8_t msg[6] = {0u, SC_CODE_SCROLL_DOWN, (uint8_t)point[0], (uint8_t)(point[0] >> 8),
                          (uint8_t)point[1], (uint8_t)(point[1] >> 8)};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    if (code == SC_CODE_4A) {
        uint8_t msg[6] = {0u, SC_CODE_4A, 0u, 0u, 0u, 0u};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    if (code == SC_CODE_CLICK) {
        uint8_t msg[6] = {0u, SC_CODE_CLICK, 0u, 0u, 0u, 0u};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    if (code == SC_CODE_CLOSE) {
        uint8_t msg[6] = {0u, SC_CODE_CLOSE, 0u, 0u, 0u, 0u};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    if (code == SC_CODE_49) {
        uint8_t msg[6] = {0u, SC_CODE_49, 0u, 0u, 0u, 0u};
        return audio_uart_master_display_refresh(SC_APP_ID, msg, 6u, 0u);
    }
    return (int32_t)code;
}

static void log_simple(uint32_t line, const char *fn, const char *msg, const char *compact)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, compact, compact);
}

uint32_t system_close_page_event_handler(void *page, uint32_t arg, uint32_t code,
                                         const g2_system_close_event_t *event)
{
    (void)page;
    (void)arg;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, page_event_fn, 0xf2u, event_msg, code);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, event_short, event_short, code);
    if (code == SC_CODE_CLICK) {
        log_simple(0xf4u, page_event_fn, clicked_msg, clicked_short);
        if (audio_uart_device_role_get() == 2u)
            return 1u;
        if (audio_uart_device_role_get() == 1u)
            system_close_handle_click();
        return 1u;
    }
    if (code == SC_CODE_CLOSE) {
        if (audio_uart_device_role_get() == 2u)
            return 1u;
        (void)system_close_dispatch_page_action_00469e66(SC_CODE_CLOSE, event);
        return 1u;
    }
    if (code == SC_CODE_SCROLL_UP) {
        log_simple(0x105u, page_event_fn, scroll_up_event_msg, scroll_up_event_short);
        if (audio_uart_device_role_get() == 2u)
            return 1u;
        (void)system_close_dispatch_page_action_00469e66(SC_CODE_SCROLL_UP, event);
        return 1u;
    }
    if (code == SC_CODE_SCROLL_DOWN) {
        log_simple(0x10du, page_event_fn, scroll_down_event_msg, scroll_down_event_short);
        if (audio_uart_device_role_get() == 2u)
            return 1u;
        (void)system_close_dispatch_page_action_00469e66(SC_CODE_SCROLL_DOWN, event);
        return 1u;
    }
    if (code == SC_CODE_4D)
        return 1u;
    if (code == SC_CODE_4E)
        return 1u;
    if (code == SC_CODE_IMU_REFLASH) {
        log_simple(0x11cu, page_event_fn, imu_msg, imu_short);
        return 1u;
    }
    return 1u;
}

/* 0x46a18c: actually builds the panel (black, 200 x 156, centred) and the bordered
 * container that holds the title, options and arrow. */
void system_close_selection_animation_0046a18c(void *parent)
{
    void *panel = audio_uart_page_43de82(parent);
    g2_system_close_panel = panel;
    audio_uart_page_43f4c0(panel, 200, g2_system_close_panel_height);
    audio_uart_page_43f0e0(panel, (audio_uart_lv_obj_width_43fd9e(parent) - 200) / 2);
    audio_uart_page_43f142(panel, (audio_uart_lv_obj_height_43fdda(parent) - g2_system_close_panel_height) / 2);
    audio_uart_page_43dfa4(panel, 0x2004u); /* CLICK_FOCUSABLE | PRESS_LOCK */
    audio_uart_page_44e368(panel, 0u);      /* LV_SCROLLBAR_MODE_OFF */
    audio_uart_page_44127e(panel, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(panel, 0xffu, 0u);
    audio_uart_page_4412ec(panel, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44131c(panel, 0, 0u);
    system_close_fifo_reset_00469bf4(panel, 0, 0u);

    void *container = audio_uart_page_43de82(panel);
    g2_system_close_container = container;
    audio_uart_page_43f4c0(container, 0xb8, g2_system_close_panel_height);
    if (audio_uart_device_role_get() == 1u)
        audio_uart_page_43f0e0(container, 0);
    else
        audio_uart_page_43f0e0(container, g2_system_close_arrow_room);
    audio_uart_page_43f142(container, 0);
    audio_uart_page_44e368(container, 0u);
    audio_uart_page_44e3ca(container, 0x0cu); /* LV_DIR_VER */
    audio_uart_page_44129e(container, 0u, 0u);
    audio_uart_page_44146a(container, 10, 0u);
    audio_uart_page_4412ec(container, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(container, 1, 0u);
    audio_uart_page_44120e(container, 0, 0u);
    audio_uart_page_44121c(container, 0, 0u);
    audio_uart_page_44122a(container, 0, 0u);
    audio_uart_page_441238(container, 0, 0u);
}

/* 0x46a2ca: size the box to the title and stack title, option 0 and option 1. */
void system_close_option_position_0046a2ca(void)
{
    if (g2_system_close_title == NULL || g2_system_close_option0 == NULL || g2_system_close_option1 == NULL)
        return;
    audio_uart_page_43f66c(g2_system_close_container);
    int32_t width = audio_uart_lv_obj_width_43fd9e(g2_system_close_title);
    int32_t title_height = audio_uart_lv_obj_height_43fdda(g2_system_close_title);
    int32_t option_height = audio_uart_lv_obj_height_43fdda(g2_system_close_option0);
    width += g2_system_close_side_pad * 2;
    audio_uart_page_43f506(g2_system_close_container, width);
    int32_t panel_width = g2_system_close_arrow_room + width;
    audio_uart_page_43f506(g2_system_close_panel, panel_width);
    void *screen = audio_uart_lv_obj_parent_44dca2(g2_system_close_panel);
    audio_uart_page_43f0e0(g2_system_close_panel, (audio_uart_lv_obj_width_43fd9e(screen) - panel_width) / 2);
    audio_uart_page_43f142(g2_system_close_panel,
                           (audio_uart_lv_obj_height_43fdda(screen) - g2_system_close_panel_height) / 2);
    audio_uart_page_43f6b8(g2_system_close_title, 2u, 0, g2_system_close_title_top); /* LV_ALIGN_TOP_MID */
    int32_t y = g2_system_close_title_gap + title_height + g2_system_close_title_top;
    audio_uart_page_43f6b8(g2_system_close_option0, 2u, 0, y);
    audio_uart_page_43f6b8(g2_system_close_option1, 2u, 0, g2_system_close_option_gap + option_height + y);
    audio_uart_page_43f66c(g2_system_close_container);
    system_close_update_selection();
}

/* Completed callback of the selection animation: replay one queued input code. */
void sc_selection_change_anim_ready_cb(void *anim)
{
    (void)anim;
    uint8_t event[10];
    log_simple(0x176u, anim_ready_fn, anim_done_msg, anim_done_short);
    g2_system_close_anim_busy = 0u;
    if (system_close_fifo_empty_00469c98() != 0u)
        return;
    audio_uart_buffer_zero(event, sizeof event, 0u);
    audio_uart_buffer_zero(event, sizeof event, 0u);
    (void)system_close_fifo_pop_00469cac(event, 5u);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, anim_ready_fn, 0x17du, pop_msg, event[0]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, pop_short, pop_short, event[0]);
    if (event[0] == SC_CODE_CLICK)
        system_close_handle_click();
    else if (event[0] == SC_CODE_SCROLL_UP)
        system_close_handle_scroll_up();
    else if (event[0] == SC_CODE_SCROLL_DOWN)
        system_close_handle_scroll_down();
    else if (event[0] == SC_CODE_CLOSE && audio_uart_device_role_get() == 1u)
        audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
}

/* 0x46a4e2: start the 200 ms (value-less) selection-change animation on the panel. */
void system_close_process_next_event_0046a4e2(void)
{
    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = g2_system_close_panel;
    anim.exec_cb = system_close_anim_exec_noop_46a3d6;
    audio_uart_lv_anim_values_4506ce(&anim, 0, 0);
    anim.duration = 200;
    anim.path_cb = audio_uart_lv_anim_default_path_450634;
    anim.completed_cb = sc_selection_change_anim_ready_cb;
    g2_system_close_anim_busy = 1u;
    (void)audio_uart_lv_anim_start_450408(&anim);
}

static void highlight(void *option, int32_t index)
{
    uint32_t color = g2_system_close_selected_index == index ? audio_uart_page_44104c(0xffffffu)
                                                             : audio_uart_page_44104c(0x444444u);
    audio_uart_page_44140e(option, color, 0u);
}

/* Put the arrow 8 px left of the selected option and grey out the others. */
void system_close_update_selection(void)
{
    if (g2_system_close_arrow == NULL)
        return;
    void *selected = NULL;
    if (g2_system_close_selected_index == 0)
        selected = g2_system_close_option0;
    else if (g2_system_close_item_count == 2 && g2_system_close_selected_index == 1)
        selected = g2_system_close_option1;
    else if (g2_system_close_item_count == 3 && g2_system_close_selected_index == 1)
        selected = g2_system_close_option1;
    else if (g2_system_close_item_count == 3 && g2_system_close_selected_index == 2)
        selected = g2_system_close_option2;
    int32_t x = 0;
    int32_t y = 0;
    if (selected != NULL) {
        int32_t sx = audio_uart_lv_obj_x_43fc70(selected);
        int32_t sy = audio_uart_lv_obj_y_43fce0(selected);
        int32_t sh = audio_uart_lv_obj_height_43fdda(selected);
        int32_t aw = audio_uart_lv_obj_width_43fd9e(g2_system_close_arrow);
        int32_t ah = audio_uart_lv_obj_height_43fdda(g2_system_close_arrow);
        x = sx - aw - 8;
        y = (sh - ah) / 2 + sy;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, update_fn, 0x1c3u, update_msg,
                           g2_system_close_selected_index, x, y);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10c00000u, update_short, update_short,
                                  g2_system_close_selected_index, x, y);
    audio_uart_page_43f09a(g2_system_close_arrow, x, y);
    if (g2_system_close_option0 != NULL)
        highlight(g2_system_close_option0, 0);
    if (g2_system_close_option1 != NULL)
        highlight(g2_system_close_option1, 1);
    if (g2_system_close_option2 != NULL && g2_system_close_item_count == 3)
        highlight(g2_system_close_option2, 2);
}

void system_close_handle_scroll_up(void)
{
    if (g2_system_close_item_count - 1 <= g2_system_close_selected_index) {
        log_simple(0x1e2u, up_fn, up_last_msg, up_last_short);
        return;
    }
    g2_system_close_selected_index++;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, up_fn, 0x1ddu, up_msg, g2_system_close_selected_index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, up_short, up_short, g2_system_close_selected_index);
    system_close_update_selection();
    system_close_process_next_event_0046a4e2();
}

void system_close_handle_scroll_down(void)
{
    if (g2_system_close_selected_index < 1) {
        log_simple(0x1f0u, down_fn, down_first_msg, down_first_short);
        return;
    }
    g2_system_close_selected_index--;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, down_fn, 0x1ebu, down_msg, g2_system_close_selected_index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, down_short, down_short, g2_system_close_selected_index);
    system_close_update_selection();
    system_close_process_next_event_0046a4e2();
}

static void log_choice(uint8_t level, uint32_t compact_level, uint32_t line, const char *msg, const char *compact)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, click_fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(compact_level, compact, compact);
}

/* Master only acts: NO closes the page, YES closes it and asks the peers to power off
 * (input event 6/0x0f, 500 ms). MINI (three-item style) is logged only. */
void system_close_handle_click(void)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, click_fn, 0x1f8u, click_msg,
                           g2_system_close_selected_index, g2_system_close_item_count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10800000u, click_short, click_short,
                                  g2_system_close_selected_index, g2_system_close_item_count);
    if (g2_system_close_item_count == 2) {
        if (g2_system_close_selected_index == 0) {
            log_choice(3u, 0x0c000000u, 0x1feu, no_msg, no_short);
            if (audio_uart_device_role_get() == 1u)
                audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
        } else if (g2_system_close_selected_index == 1) {
            log_choice(3u, 0x0c000000u, 0x203u, yes_msg, yes_short);
            if (audio_uart_device_role_get() == 1u) {
                audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
                (void)async_send_input_event_to_peers_45accc(6u, 0x0fu, 0u, 500u);
            }
        }
    } else if (g2_system_close_item_count == 3) {
        if (g2_system_close_selected_index == 0) {
            log_choice(4u, 0x10000000u, 0x20cu, no_msg, no_short);
            if (audio_uart_device_role_get() == 1u)
                audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
        } else if (g2_system_close_selected_index == 1) {
            log_choice(4u, 0x10000000u, 0x211u, mini_msg, mini_short);
        } else if (g2_system_close_selected_index == 2) {
            log_choice(4u, 0x10000000u, 0x214u, yes_msg, yes_short);
            if (audio_uart_device_role_get() == 1u) {
                audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
                (void)async_send_input_event_to_peers_45accc(6u, 0x0fu, 0u, 500u);
            }
        }
    }
}

static void *option_label(const char *key)
{
    void *label = audio_uart_page_499416(g2_system_close_container);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(key, audio_uart_page_460084(key)));
    audio_uart_page_44143e(label, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_43f506(label, 0x3fffffff);   /* LV_SIZE_CONTENT */
    audio_uart_page_43f568(label, 0x3fffffff);
    audio_uart_page_43ded4(label, 0x10000u);
    audio_uart_page_43dfa4(label, 0x10u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    return label;
}

/* Style 1 gets NO/YES labels; any other style only sets item_count = 3. */
void system_close_create_options(uint32_t style)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, options_fn, 0x220u, options_msg, style);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, options_short, options_short, style);
    g2_system_close_item_count = style == 1u ? 2 : 3;
    g2_system_close_arrow = audio_uart_page_498668(g2_system_close_container);
    audio_uart_page_498680(g2_system_close_arrow, g2_system_close_arrow_image);
    audio_uart_page_43f4c0(g2_system_close_arrow, 0x12, 0x12);
    if (style == 1u) {
        g2_system_close_option0 = option_label(id_no);
        g2_system_close_option1 = option_label(id_yes);
    }
    g2_system_close_selected_index = 0;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, options_fn, 0x25bu, created_msg,
                           g2_system_close_item_count, g2_system_close_selected_index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10800000u, created_short, created_short,
                                  g2_system_close_item_count, g2_system_close_selected_index);
}

/* Refresh with no data builds the popup for the requested style; a refresh record
 * {0, code, ...} is executed now or queued while the selection animation runs. */
void system_close_ReflashEventHandler(const uint8_t *data, uint32_t length)
{
    if (data == NULL || length == 0u) {
        uint8_t style = audio_system_close_selected_20075026;
        if (style != 1u) {
            if (audio_log_flags() & 2u)
                audio_log_extended(2u, module_tag, source_file, reflash_fn, 0x28au, unknown_msg, style);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compress_log_output(0x08400000u, unknown_short, unknown_short, style);
            return;
        }
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, reflash_fn, 0x263u, reflash_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, reflash_short, reflash_short);
        audio_uart_page_44d878(g2_system_close_container);
        void *title = audio_uart_page_499416(g2_system_close_container);
        g2_system_close_title = title;
        audio_uart_page_49942e(title, audio_uart_page_45fffe(id_popup, audio_uart_page_460084(id_popup)));
        audio_uart_page_43f506(title, 0x3fffffff);
        audio_uart_page_43f568(title, 0x3fffffff);
        audio_uart_page_43ded4(title, 0x10000u);
        audio_uart_page_43dfa4(title, 0x10u);
        audio_uart_page_44143e(title, audio_uart_ring_secondary_head_cell, 0u);
        audio_uart_page_44140e(title, audio_uart_page_44104c(0xffffffu), 0u);
        system_close_create_options(1u);
        system_close_option_position_0046a2ca();
        g2_system_close_popup_shown = 1u;
        return;
    }
    if (data[0] != 0u)
        return;
    uint8_t code = data[1];
    if (g2_system_close_anim_busy != 0u) {
        (void)system_close_fifo_push_00469c26(data + 1, 5u);
        return;
    }
    if (code == SC_CODE_CLICK)
        system_close_handle_click();
    else if (code == SC_CODE_SCROLL_UP)
        system_close_handle_scroll_up();
    else if (code == SC_CODE_SCROLL_DOWN)
        system_close_handle_scroll_down();
    else if (code == SC_CODE_CLOSE && audio_uart_device_role_get() == 1u)
        audio_system_alert_close_464c36(SC_APP_ID, 0u, 0u, 0u);
}

/* 0x46ae9c: send the 5-byte open record {style, app_id (LE)} to the page's data handler. */
void system_close_page_factory_0046ae9c(uint32_t style, int32_t app_id)
{
    uint8_t record[10];
    audio_uart_buffer_zero(record, sizeof record, 0u);
    audio_uart_buffer_zero(record, sizeof record, 0u);
    record[0] = (uint8_t)style;
    record[1] = (uint8_t)app_id;
    record[2] = (uint8_t)(app_id >> 8);
    record[3] = (uint8_t)(app_id >> 16);
    record[4] = (uint8_t)(app_id >> 24);
    (void)audio_uart_input_event_send_464d1c(SC_APP_ID, record, 5u, 0u);
}

static void reset_page_state(void)
{
    system_close_set_style_00469d24();
    g2_system_close_selected_index = 0;
    g2_system_close_item_count = 2;
    g2_system_close_arrow = NULL;
    g2_system_close_option0 = NULL;
    g2_system_close_option2 = NULL;
    g2_system_close_option1 = NULL;
}

uint32_t system_close_ui_event_handler(uint32_t event, const uint8_t *data, uint32_t length, void *parent)
{
    if (event == 2u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, ui_fn, 0x2c9u, startup_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, startup_short, startup_short);
        g2_system_close_anim_busy = 0u;
        reset_page_state();
        system_close_selection_animation_0046a18c(parent);
        ((void **)(void *)&audio_uart_registry_context_20003bf0)[1] = g2_system_close_panel;
    } else if (event == 3u) {
        system_close_ReflashEventHandler(data, length);
    } else if (event == 4u) {
        /* periodic tick: nothing to do */
    } else if (event == 5u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module_tag, source_file, ui_fn, 0x2d9u, exit_msg);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x10000000u, exit_short, exit_short);
        g2_system_close_anim_busy = 0u;
        if (g2_system_close_panel != NULL)
            (void)audio_uart_lv_style_unlink_450500(g2_system_close_panel, NULL);
        reset_page_state();
    }
    return 0u;
}
