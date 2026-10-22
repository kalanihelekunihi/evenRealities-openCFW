/* Menu page data, event FIFO, BLE configuration and scroll/rubber-band animation callbacks,
 * stock D:\01_workspace\s200_ap510b_iar_git\app\gui\menu\menu_page.c (log tag "menu.page").
 * Native 0x46015a..0x46155a (literal pools 0x46061c, 0x460d5c, 0x460e00, 0x460fac,
 * 0x461028, 0x4611b0, 0x4612f0, 0x461348, 0x46155c). The lock initialiser 0x460178 is in
 * rtos/rtos-glue-gaps/menu_page_mutex.c; menu_inject_event 0x461620, the absolute jump
 * 0x462594, the focus-style refresh 0x462db6 and the page event handler 0x46327e follow
 * this range.
 *
 * Menu_common_data_handler (0x460638) is registry entry 12 of the UI registry (ROM 0x6a4570,
 * system/ui-registry/ui_registry_table.c) with context RAM 0x20002ca8, whose +0x0c word is
 * the page animation time. Source 0 is the phone (BLE protobuf, nanopb descriptor ROM
 * 0x779694), source 4 is the peer/UI two-byte form {0, anim_time} sent by 0x460424. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define MENU_ITEM_MAX        20u
#define MENU_BUILTIN_COUNT   8u
#define MENU_VISIBLE_ITEMS   5
#define MENU_ANIM_TIME_RESUME 250u
#define MENU_RUBBER_BAND_PX  30
#define MENU_PAGE_ID         3u    /* page id passed to 0x45f840 and to the sync channel */
#define CUSTOM_TEXT_RES      0xffeu
#define CUSTOM_APP_TYPE      1u
#define MENU_CTX_SEND_DATA   3u    /* which_Msg_Ctx sendData_tag */
#define MENU_CTX_RESPONSE    4u
#define MENU_SRC_BLE         0
#define MENU_SRC_UI          4

/* Menu page item (displayed table RAM 0x2006a8fc, external table RAM 0x2006ad0c,
 * built-in table ROM 0x6c2198); same layout as service_kvdb_module_configure.c. */
typedef struct {
    const void *icon;      /* +0x00 lv_image_dsc_t */
    char text[32];         /* +0x04 i18n key or custom name */
    uint32_t text_res;     /* +0x24 0xffe for custom apps */
    uint8_t app_type;      /* +0x28 */
    uint8_t reserved[3];
    int32_t icon_num;      /* +0x2c */
    int32_t app_id;        /* +0x30 */
} g2_menu_page_item_t;
_Static_assert(sizeof(g2_menu_page_item_t) == 0x34, "menu page item");

/* Decoded phone item (nanopb), 44 bytes like the kvMenuConfigureValue record item. */
typedef struct {
    uint32_t app_type;     /* +0x00 0 = built-in */
    int32_t icon_num;      /* +0x04 */
    char text_name[32];    /* +0x08 */
    int32_t app_id;        /* +0x28 */
} g2_menu_pb_item_t;
_Static_assert(sizeof(g2_menu_pb_item_t) == 44, "menu pb item");

/* Menu protobuf message (decode target RAM 0x2037a9a0, response RAM 0x2037ad1c; 0x37c bytes). */
typedef struct {
    uint8_t cmd;              /* +0x00 0 = configure */
    uint8_t magic_random;     /* +0x01 echoed in the response */
    uint16_t which_msg_ctx;   /* +0x02 3 = sendData, 4 = response */
    union {
        struct {
            uint32_t item_total_num;              /* +0x04 */
            uint16_t item_count;                  /* +0x08 */
            uint8_t pad_0a[2];
            g2_menu_pb_item_t items[MENU_ITEM_MAX]; /* +0x0c */
        } send_data;
        uint32_t response_status;                 /* +0x04 0 ok, 1 failed */
    } ctx;
} g2_menu_pb_msg_t;
_Static_assert(sizeof(g2_menu_pb_msg_t) == 0x37c, "menu pb message");
_Static_assert(offsetof(g2_menu_pb_msg_t, ctx.send_data.items) == 0x0c, "items at +0x0c");

/* Event FIFO (RAM 0x2006ffd8): 256-byte ring with byte indices. */
typedef struct {
    uint8_t data[256];     /* +0x000 */
    uint16_t head;         /* +0x100 write index */
    uint16_t tail;         /* +0x102 read index */
    uint16_t count;        /* +0x104 */
} g2_menu_event_fifo_t;
_Static_assert(offsetof(g2_menu_event_fifo_t, count) == 0x104, "fifo count at +0x104");

/* UI registry context of the menu page (RAM 0x20002ca8). */
typedef struct {
    uint8_t reserved_00[0x0c];
    uint32_t anim_time;    /* +0x0c */
} g2_menu_registry_context_t;

/* Registered page-stack entry returned by 0x45f840. */
typedef struct {
    uint8_t reserved_00[0x0c];
    uint32_t anim_time;    /* +0x0c */
} g2_page_entry_t;

/* LVGL 9.3 lv_anim_t as laid out on the stack by this unit (0x60 bytes). */
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
    uint32_t reverse_delay;                     /* +0x38 */
    uint32_t reverse_duration;                  /* +0x3c */
    uint8_t reserved_40[0x20];
} g2_lv_anim_t;
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "lv_anim_t frame");

/* nanopb pb_istream_t / pb_ostream_t */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;    /* +0x0c */
} g2_pb_istream_t;
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} g2_pb_ostream_t;

/* RAM / ROM */
extern void *g2_menu_page_mutex;                                  /* RAM 0x200746e4 */
extern int32_t g2_menu_configure_dirty;                           /* RAM 0x200746e8, saved by 0x460580 */
extern void *g2_menu_focus_anim_obj;                              /* RAM 0x200746ec */
extern void *g2_menu_list_obj;                                    /* RAM 0x200746f4 scrolled list */
extern void *g2_menu_content_container;                           /* RAM 0x200746f8 */
extern int32_t g2_menu_use_ext_items;                             /* RAM 0x200746fc */
extern int32_t g2_menu_ext_item_count;                            /* RAM 0x20074700 */
extern int32_t g2_menu_item_count;                                /* RAM 0x20074704 */
extern int32_t g2_menu_current_index;                             /* RAM 0x20074708 */
extern int32_t g2_menu_scroll_offset;                             /* RAM 0x2007470c, in items */
extern volatile uint8_t g2_menu_anim_in_progress;                 /* RAM 0x20074fe4 */
extern g2_menu_page_item_t g2_menu_display_items[MENU_ITEM_MAX];  /* RAM 0x2006a8fc */
extern g2_menu_page_item_t g2_menu_page_items[MENU_ITEM_MAX];     /* RAM 0x2006ad0c */
extern g2_menu_event_fifo_t g2_menu_event_fifo;                   /* RAM 0x2006ffd8 */
extern g2_menu_pb_msg_t g2_menu_decode_msg;                       /* RAM 0x2037a9a0 */
extern g2_menu_pb_msg_t g2_menu_response_msg;                     /* RAM 0x2037ad1c */
extern uint8_t g2_menu_encode_buffer[0x432];                      /* RAM 0x20378540 */
extern g2_menu_registry_context_t audio_uart_registry_context_20002ca8; /* RAM 0x20002ca8 */
extern uint32_t audio_uart_display_audio_handle;                  /* RAM 0x200744d0 page manager */
extern uint32_t g2_audio_log_event_handle;                        /* RAM 0x20074570 osEventFlagsId_t */
extern const int32_t g2_menu_item_height;                         /* ROM 0x78f2c8 = 50 */
extern const g2_menu_page_item_t g2_menu_builtin_apps[MENU_BUILTIN_COUNT]; /* ROM 0x6c2198 */
extern const uint8_t g2_menu_custom_app_icon[];                   /* ROM 0x76b7bc */
extern const uint8_t g2_menu_pb_msgdesc[];                        /* ROM 0x779694 nanopb descriptor */

/* Callees */
extern uint32_t audio_log_flags(void);                            /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t value); /* memset 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern uint32_t g2_log_module_length(const char *text);           /* strlen 0x44a43c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);     /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                       /* 0x44981c */
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags);     /* 0x4495e4 */
extern void menu_page_mutex_init_460178(void);
extern uint32_t audio_uart_page_460084(const char *key);          /* i18n index of key */
extern uint32_t audio_uart_page_45fffe(const char *key, uint32_t index); /* localized text */
extern void *audio_uart_display_audio_find_45f840(void *state, uint32_t id);
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf, uint32_t len); /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dst); /* pb_decode 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src); /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475b14 */
extern int32_t SVC_KvdbWriteMenuConfigureValue(void);             /* 0x49292e */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern uint8_t audio_uart_device_role_get(void);                  /* 0x45a568 */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t context);
extern void lv_obj_set_style_transform_scale_x_4411f2(void *obj, int32_t value, uint32_t selector);
extern void lv_obj_set_style_transform_scale_y_441200(void *obj, int32_t value, uint32_t selector);
extern void audio_uart_lv_anim_init_4503d6(void *anim);
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern void *audio_uart_lv_anim_start_450408(void *anim);
extern int32_t audio_uart_lv_anim_default_path_450634(void *anim); /* lv_anim_path_linear */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);        /* lv_anim_path_ease_out */
extern int32_t audio_uart_lv_anim_path_450688(void *anim);        /* lv_anim_path_ease_in_out */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);             /* lv_obj_get_y */
extern void audio_uart_page_43f142(void *obj, int32_t y);         /* lv_obj_set_y */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);             /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *obj);        /* lv_obj_get_scroll_top */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t animated);
extern void menu_inject_event_461620(uint32_t event);             /* 0 up, 1 down, 2 select */
extern void menu_inject_event_absolute_462594(uint8_t index);
extern void menu_update_item_styles_462db6(void);
extern void menu_item_styles_hook_462db4(void);                   /* empty body in stock */

/* Strings */
static const char menu_module[] = "menu.page"; /* ROM 0x78b5b8 */
static const char menu_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\menu\\menu_page.c"; /* ROM 0x70ca64 */
static const char fn_lock[] = "menu_lock_data";                         /* ROM 0x787a80 */
static const char fn_unlock[] = "menu_unlock_data";                     /* ROM 0x781250 */
static const char fn_resume[] = "resume_menu_anim_time";                /* ROM 0x7796ac */
static const char fn_response[] = "menu_response_info_cmd";             /* ROM 0x7796c4 */
static const char fn_save[] = "MenuConfigureValueSaveToFlash";          /* ROM 0x762250 */
static const char fn_handler[] = "Menu_common_data_handler";            /* ROM 0x76e034 */
static const char fn_calc[] = "calculate_scroll_position_for_item";     /* ROM 0x756a08 */
static const char fn_scroll_done[] = "scroll_anim_complete_cb";         /* ROM 0x7796dc */
static const char fn_rubber_done[] = "rubber_band_anim_complete_cb";    /* ROM 0x7622b0 */
static const char fn_focus_done[] = "focus_change_anim_ready_cb";       /* ROM 0x76e06c */
static const char fn_rubber[] = "trigger_rubber_band_effect";           /* ROM 0x76e088 */
static const char str_none[] = "(none)";                                /* ROM 0x78dcbc */

/* Each message goes to the extended log (plain string) and the compressed log
 * ("[menu.page]" copy). ROM comments give plain / compact addresses. */
#define MENU_LOG(fn, level, line, mask, fmt, ...) do { \
    if ((audio_log_flags() & 2u) != 0u) \
        audio_log_extended((level), menu_module, menu_source, (fn), (line), fmt, ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u) \
        (void)compress_log_output((mask), "[menu.page]" fmt, "[menu.page]" fmt, ##__VA_ARGS__); \
} while (0)

#define ITEM_TEXT(item) \
    ((const char *)(uintptr_t)audio_uart_page_45fffe((item)->text, audio_uart_page_460084((item)->text)))

/* LVGL lv_obj_set_style_transform_scale (static inline, emitted out of line here). */
void menu_obj_set_style_transform_scale_46015a(void *obj, int32_t value, uint32_t selector)
{
    lv_obj_set_style_transform_scale_x_4411f2(obj, value, selector);
    lv_obj_set_style_transform_scale_y_441200(obj, value, selector);
}

/* menu_lock_data */
void menu_page_mutex_lock_46018e(void)
{
    if (g2_menu_page_mutex == NULL) {
        /* "menu_lock_data: mutex is NULL" ROM 0x762210 / 0x73ff20 */
        MENU_LOG(fn_lock, 1u, 0x4du, 0x04000000u, "menu_lock_data: mutex is NULL");
        return;
    }
    (void)osMutexAcquire(g2_menu_page_mutex, 0xffffffffu);
}

/* menu_unlock_data */
void menu_page_mutex_unlock_4601ea(void)
{
    if (g2_menu_page_mutex == NULL) {
        /* ROM 0x762230 / 0x73ff4c */
        MENU_LOG(fn_unlock, 1u, 0x56u, 0x04000000u, "menu_unlock_data: mutex is NULL");
        return;
    }
    (void)osMutexRelease(g2_menu_page_mutex);
}

/* Append len bytes: -3 bad argument, -1 not enough room (nothing written), 0 ok. */
int32_t menu_event_fifo_push_460242(const uint8_t *data, uint16_t len)
{
    g2_menu_event_fifo_t *fifo = &g2_menu_event_fifo;
    if (data == NULL || len == 0u)
        return -3;
    if ((uint16_t)(256u - fifo->count) < len)
        return -1;
    for (uint16_t i = 0u; i < len; i++) {
        fifo->data[fifo->head] = data[i];
        fifo->head = (uint16_t)((fifo->head + 1) % 256);
        fifo->count++;
    }
    return 0;
}

bool menu_event_fifo_is_empty_4602b6(void)
{
    return g2_menu_event_fifo.count == 0u;
}

/* Remove up to len bytes: -3 bad argument, 0 when empty, otherwise bytes copied. */
int32_t menu_event_fifo_pop_4602ca(uint8_t *out, uint16_t len)
{
    g2_menu_event_fifo_t *fifo = &g2_menu_event_fifo;
    if (out == NULL || len == 0u)
        return -3;
    if (fifo->count == 0u)
        return 0;
    if (len >= fifo->count)
        len = fifo->count;
    for (uint16_t i = 0u; i < len; i++) {
        out[i] = fifo->data[fifo->tail];
        fifo->tail = (uint16_t)((fifo->tail + 1) % 256);
        fifo->count--;
    }
    return len;
}

void menu_event_fifo_reset_460344(void)
{
    g2_menu_event_fifo_t *fifo = &g2_menu_event_fifo;
    fifo->head = 0u;
    fifo->tail = 0u;
    fifo->count = 0u;
    audio_uart_buffer_zero(fifo, sizeof(fifo->data), 0u);
}

void menu_set_anim_time_46036a(uint8_t anim_time)
{
    audio_uart_registry_context_20002ca8.anim_time = anim_time;
}

/* Restore the 250 ms page animation in the registry and in the registered menu page. */
void resume_menu_anim_time_460374(void)
{
    /* ROM 0x76e018 / 0x74b234 */
    MENU_LOG(fn_resume, 3u, 0x117u, 0x0c400000u, "resume menu anim time to %d", MENU_ANIM_TIME_RESUME);
    audio_uart_registry_context_20002ca8.anim_time = MENU_ANIM_TIME_RESUME;
    if (audio_uart_display_audio_handle != 0u) {
        g2_page_entry_t *entry = (g2_page_entry_t *)audio_uart_display_audio_find_45f840(
            (void *)(uintptr_t)audio_uart_display_audio_handle, MENU_PAGE_ID);
        if (entry != NULL) {
            entry->anim_time = MENU_ANIM_TIME_RESUME;
            /* ROM 0x74b25c / 0x72ab14 */
            MENU_LOG(fn_resume, 4u, 0x11fu, 0x10000000u, "update registered page anim_time to 250");
        }
    }
}

/* Send {0, anim_time} to the peer menu handler (source 4 of 0x460638). Caller 0x45c8ba. */
void menu_anim_time_sync_send_460424(uint8_t anim_time)
{
    uint8_t frame[2];
    audio_uart_buffer_zero(frame, sizeof frame, 0u);
    frame[0] = 0u;
    frame[1] = anim_time;
    (void)audio_sync_send_to_both_ext_464f76(MENU_PAGE_ID, frame, sizeof frame, 0u, 4u);
}

/* Fill icon/text/text_res/app_type of a built-in app; 0 found, -1 unknown id. The text
 * copy is strlen bytes without the terminator (callers clear the table first). */
int32_t menu_builtin_app_info_get_460450(int32_t app_id, const void **icon, char *text,
                                         uint32_t *text_res, uint8_t *app_type)
{
    for (uint32_t i = 0u; i < MENU_BUILTIN_COUNT; i++) {
        const g2_menu_page_item_t *app = &g2_menu_builtin_apps[i];
        if (app->app_id != app_id)
            continue;
        *icon = app->icon;
        (void)audio_queue_copy_bytes(text, app->text, g2_log_module_length(app->text));
        *text_res = app->text_res;
        *app_type = app->app_type;
        return 0;
    }
    return -1;
}

/* Encode the response {cmd 1, magicRandom, which 4, status} and send it as PB type 1 / cmd 3. */
uint32_t menu_response_info_cmd_4604c2(uint8_t magic_random, uint8_t status)
{
    g2_menu_pb_msg_t *msg = &g2_menu_response_msg;
    g2_pb_ostream_t tmp;
    g2_pb_ostream_t stream;

    audio_uart_buffer_zero(msg, sizeof *msg, 0u);
    audio_uart_buffer_zero(g2_menu_encode_buffer, sizeof g2_menu_encode_buffer, 0u);
    msg->cmd = 1u;
    msg->magic_random = magic_random;
    msg->which_msg_ctx = MENU_CTX_RESPONSE;
    msg->ctx.response_status = status;
    audio_pb_ostream_from_buffer(&tmp, g2_menu_encode_buffer, sizeof g2_menu_encode_buffer);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if (audio_pb_encode(&stream, g2_menu_pb_msgdesc, msg) == 0u) {
        /* ROM 0x73ff78 / 0x720360 */
        MENU_LOG(fn_response, 1u, 0x147u, 0x04000000u, "menu page response info cmd encode failed");
        return 0u;
    }
    return Thread_MsgPbTxByBle(1u, 3u, g2_menu_encode_buffer, (uint16_t)stream.bytes_written);
}

/* Persist the phone-supplied menu once it changed (caller 0x448f2e). */
void menu_configure_value_save_to_flash_460580(void)
{
    if (g2_menu_configure_dirty != 1)
        return;
    /* ROM 0x762270 / 0x73ffa4 */
    MENU_LOG(fn_save, 3u, 0x158u, 0x0c000000u, "MenuConfigureValueSaveToFlash");
    if (SVC_KvdbWriteMenuConfigureValue() != 0) {
        /* ROM 0x74b284 / 0x735594 */
        MENU_LOG(fn_save, 1u, 0x15bu, 0x04000000u, "MenuConfigureValueSaveToFlash failed");
    }
    g2_menu_configure_dirty = 0;
}

/* Menu_common_data_handler: returns 0, or 0xffffffff (-1) when a phone request is rejected. */
uint32_t audio_uart_registry_callback_460638(int32_t source, const uint8_t *data, uint32_t len)
{
    /* ROM 0x762290 / 0x74b2ac */
    MENU_LOG(fn_handler, 4u, 0x182u, 0x10400000u, "menu page recv data len = %d", len);
    menu_page_mutex_init_460178();

    if (source == MENU_SRC_UI) {
        /* ROM 0x74b2d4 / 0x72ab48 */
        MENU_LOG(fn_handler, 4u, 0x185u, 0x10400000u, "menu page recv data from UI, len = %d", len);
        if (len == 2u) {
            uint8_t anim_time = data[1];
            if (data[0] == 0u) {
                /* ROM 0x76e050 / 0x75699c */
                MENU_LOG(fn_handler, 4u, 0x18bu, 0x10400000u, "set menu anim time to %d", anim_time);
                menu_set_anim_time_46036a(anim_time);
            }
        }
        return 0u;
    }
    if (source != MENU_SRC_BLE)
        return 0u;

    /* ROM 0x74b2fc / 0x72ab7c */
    MENU_LOG(fn_handler, 4u, 0x193u, 0x10400000u, "menu page recv data from BLE, len = %d", len);
    g2_menu_pb_msg_t *msg = &g2_menu_decode_msg;
    g2_pb_istream_t tmp;
    g2_pb_istream_t stream;
    audio_uart_buffer_zero(msg, sizeof *msg, 0u);
    audio_uart_pb_stream_init(&tmp, data, len);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_menu_pb_msgdesc, msg) == 0u) {
        /* ROM 0x7569c0 / 0x73ffd0 */
        MENU_LOG(fn_handler, 1u, 0x198u, 0x04400000u, "menu protobuf decode failed: %s\n",
                 stream.errmsg != NULL ? stream.errmsg : str_none);
        return 0xffffffffu;
    }

    uint8_t cmd = msg->cmd;
    uint8_t magic = msg->magic_random;
    uint16_t which = msg->which_msg_ctx;
    /* ROM 0x6ee418 / 0x6e4220 */
    MENU_LOG(fn_handler, 4u, 0x19eu, 0x10c00000u,
             "menu page recv data from BLE, cmd = %d, magicRandom = %d, which_Msg_Ctx = %d",
             cmd, magic, which);
    if (cmd != 0u) {
        /* ROM 0x7355f4 / 0x7163a8 */
        MENU_LOG(fn_handler, 1u, 0x1cfu, 0x04400000u, "menu page recv data from BLE, unknown cmd = %d", cmd);
        return 0u;
    }
    if (which != MENU_CTX_SEND_DATA) {
        (void)menu_response_info_cmd_4604c2(magic, 1u);
        /* ROM 0x6e8a88 / 0x6ddc54 */
        MENU_LOG(fn_handler, 1u, 0x1c9u, 0x04400000u,
                 "menu page recv data from BLE, which_Msg_Ctx is not sendData_tag, which_Msg_Ctx = %d",
                 which);
        return 0xffffffffu;
    }

    if (msg->ctx.send_data.item_count != msg->ctx.send_data.item_total_num) {
        /* ROM 0x6db100 / 0x6d7a44 */
        MENU_LOG(fn_handler, 1u, 0x1a6u, 0x04800000u,
                 "menu page recv data from BLE, item_count != item_total_num, item_count = %d, item_total_num = %d",
                 msg->ctx.send_data.item_count, msg->ctx.send_data.item_total_num);
        (void)menu_response_info_cmd_4604c2(magic, 1u);
        return 0xffffffffu;
    }

    menu_page_mutex_lock_46018e();
    audio_uart_buffer_zero(g2_menu_page_items, sizeof g2_menu_page_items, 0u);
    for (int32_t i = 0; i < (int32_t)msg->ctx.send_data.item_count; i++) {
        const g2_menu_pb_item_t *src = &msg->ctx.send_data.items[i];
        g2_menu_page_item_t *dst = &g2_menu_page_items[i];
        /* ROM 0x7569e4 / 0x7355c4 (lines 0x1ad, 0x1b7, 0x1be) */
        MENU_LOG(fn_handler, 3u, 0x1adu, 0x0cc00000u, "text = %s,app_id = %d,app_type = %d",
                 ITEM_TEXT(dst), dst->app_id, dst->app_type);
        if (src->app_type == 0u) {
            if (menu_builtin_app_info_get_460450(src->app_id, &dst->icon, dst->text,
                                                 &dst->text_res, &dst->app_type) != 0) {
                /* ROM 0x6fb4a4 / 0x6e8a34 */
                MENU_LOG(fn_handler, 1u, 0x1b1u, 0x04400000u,
                         "menu page recv data from BLE, get builtin app info failed, app_id = %d",
                         src->app_id);
                (void)menu_response_info_cmd_4604c2(magic, 1u);
                menu_page_mutex_unlock_4601ea();
                return 0xffffffffu;
            }
            dst->app_id = src->app_id;
            MENU_LOG(fn_handler, 3u, 0x1b7u, 0x0cc00000u, "text = %s,app_id = %d,app_type = %d",
                     ITEM_TEXT(dst), dst->app_id, dst->app_type);
        } else {
            dst->app_id = src->app_id;
            dst->text_res = CUSTOM_TEXT_RES;
            dst->app_type = CUSTOM_APP_TYPE;
            dst->icon = g2_menu_custom_app_icon;
            (void)audio_queue_copy_bytes(dst->text, src->text_name, g2_log_module_length(src->text_name));
            MENU_LOG(fn_handler, 3u, 0x1beu, 0x0cc00000u, "text = %s,app_id = %d,app_type = %d",
                     ITEM_TEXT(dst), dst->app_id, dst->app_type);
        }
    }
    g2_menu_use_ext_items = 1;
    g2_menu_ext_item_count = msg->ctx.send_data.item_count;
    g2_menu_configure_dirty = 1;
    (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle, 4u);
    menu_page_mutex_unlock_4601ea();
    (void)menu_response_info_cmd_4604c2(magic, 0u);
    return 0u;
}

/* Scroll position (px) that brings item_index into view, clamped to [0, max_scroll];
 * max_scroll = item_height * (item_count - 5 visible). Only the log uses item_index. */
int32_t menu_calculate_scroll_position_for_item_460d6c(int32_t item_index)
{
    int32_t target = g2_menu_item_height * g2_menu_scroll_offset;
    int32_t max_scroll = g2_menu_item_height * (g2_menu_item_count - MENU_VISIBLE_ITEMS);
    if (max_scroll < 0)
        max_scroll = 0;
    if (max_scroll < target)
        target = max_scroll;
    if (target < 0)
        target = 0;
    /* ROM 0x6e8adc / 0x6ddcb4 */
    MENU_LOG(fn_calc, 4u, 0x1f9u, 0x11000000u,
             "Calculate scroll: item_index=%d, scroll_offset=%d, target_scroll=%d, max_scroll=%d",
             item_index, g2_menu_scroll_offset, target, max_scroll);
    return target;
}

/* Replay one input queued while an animation ran (5-byte records: code, argument). */
static void menu_execute_fifo_event(const uint8_t *event)
{
    uint8_t argument = event[1];
    switch (event[0]) {
    case 0x0au:
        menu_inject_event_461620(2u);
        break;
    case 0x44u:
        menu_inject_event_461620(1u);
        break;
    case 0x45u:
        menu_inject_event_461620(0u);
        break;
    case 0x46u:
        menu_inject_event_absolute_462594(argument);
        break;
    case 0x48u:
        if (audio_uart_device_role_get() == 1u)
            audio_system_alert_close_464c36(3u, 0u, 0u, 0u);
        break;
    default:
        break;
    }
}

/* ROM 0x73fffc / 0x72abb0 */
#define MENU_POP_AND_EXECUTE(fn, line, event) do { \
    (void)menu_event_fifo_pop_4602ca((event), 5u); \
    MENU_LOG((fn), 4u, (line), 0x10400000u, "Pop event from fifo and execute, code=%d", (event)[0]); \
    menu_execute_fifo_event(event); \
} while (0)

void menu_scroll_anim_complete_cb_460e24(void)
{
    int32_t scroll = audio_uart_lv_scroll_top_44e4aa(g2_menu_list_obj);
    int32_t expected = menu_calculate_scroll_position_for_item_460d6c(g2_menu_current_index);
    /* ROM 0x7163e4 / 0x6fb4ec */
    MENU_LOG(fn_scroll_done, 4u, 0x204u, 0x11000000u,
             "Animation complete: index=%d (%s), scroll=%d, expected=%d",
             g2_menu_current_index, ITEM_TEXT(&g2_menu_display_items[g2_menu_current_index]),
             scroll, expected);
    menu_update_item_styles_462db6();
    menu_item_styles_hook_462db4();
    g2_menu_anim_in_progress = 0u;
    if (!menu_event_fifo_is_empty_4602b6()) {
        uint8_t event[10];
        audio_uart_buffer_zero(event, sizeof event, 0u);
        MENU_POP_AND_EXECUTE(fn_scroll_done, 0x20cu, event);
    }
}

/* lv_anim exec callback: lv_obj_scroll_to_y(obj, y, LV_ANIM_OFF). */
void menu_scroll_anim_exec_cb_460fb4(void *obj, int32_t y)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, y, 0u);
}

/* lv_anim completed callback wrapper. */
void menu_scroll_anim_completed_460fbe(void *anim)
{
    (void)anim;
    menu_scroll_anim_complete_cb_460e24();
}

/* Animate obj's scroll position to target_y over duration ms (ease-in-out). */
void menu_scroll_anim_start_460fc6(void *obj, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = obj;
    audio_uart_lv_anim_values_4506ce(&anim, audio_uart_lv_obj_y_44e498(obj), target_y);
    anim.duration = duration;
    anim.exec_cb = menu_scroll_anim_exec_cb_460fb4;
    anim.path_cb = audio_uart_lv_anim_path_450688;
    anim.completed_cb = menu_scroll_anim_completed_460fbe;
    g2_menu_anim_in_progress = 1u;
    (void)audio_uart_lv_anim_start_450408(&anim);
}

void menu_rubber_band_anim_complete_cb_461044(void *anim)
{
    (void)anim;
    /* ROM 0x7622d0 / 0x740028 */
    MENU_LOG(fn_rubber_done, 4u, 0x243u, 0x10000000u, "Rubber band animation complete");
    if (g2_menu_content_container != NULL) {
        int32_t y = audio_uart_lv_obj_y_43fce0(g2_menu_content_container);
        if (y != 0) {
            /* ROM 0x716420 / 0x6fb534 */
            MENU_LOG(fn_rubber_done, 2u, 0x249u, 0x08400000u,
                     "Content container Y not zero after animation: %d, resetting", y);
            audio_uart_page_43f142(g2_menu_content_container, 0);
        }
    }
    g2_menu_anim_in_progress = 0u;
    if (!menu_event_fifo_is_empty_4602b6()) {
        uint8_t event[10];
        audio_uart_buffer_zero(event, sizeof event, 0u);
        MENU_POP_AND_EXECUTE(fn_rubber_done, 0x252u, event);
    }
}

/* Exec callback of the focus-change timing animation: nothing to animate. */
void menu_focus_anim_exec_noop_4611d4(void *var, int32_t value)
{
    (void)var;
    (void)value;
}

void menu_focus_change_anim_ready_cb_4611d6(void *anim)
{
    (void)anim;
    /* ROM 0x7622f0 / 0x740054 */
    MENU_LOG(fn_focus_done, 4u, 0x272u, 0x10000000u, "Focus change animation complete");
    g2_menu_anim_in_progress = 0u;
    if (!menu_event_fifo_is_empty_4602b6()) {
        uint8_t event[10];
        audio_uart_buffer_zero(event, sizeof event, 0u);
        audio_uart_buffer_zero(event, sizeof event, 0u); /* stock clears twice */
        MENU_POP_AND_EXECUTE(fn_focus_done, 0x279u, event);
    }
}

/* 200 ms no-op animation that marks the menu busy while the focus restyles. */
void menu_focus_change_anim_start_4612f8(void)
{
    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = g2_menu_focus_anim_obj;
    anim.exec_cb = menu_focus_anim_exec_noop_4611d4;
    audio_uart_lv_anim_values_4506ce(&anim, 0, 0);
    anim.duration = 200;
    anim.path_cb = audio_uart_lv_anim_default_path_450634;
    anim.completed_cb = menu_focus_change_anim_ready_cb_4611d6;
    g2_menu_anim_in_progress = 1u;
    (void)audio_uart_lv_anim_start_450408(&anim);
}

/* lv_anim exec callback: lv_obj_set_y. */
void menu_rubber_band_anim_exec_cb_461374(void *obj, int32_t y)
{
    audio_uart_page_43f142(obj, y);
}

/* Overscroll bounce: at_top stretches the content container down by 30 px and back;
 * otherwise the list scrolls 30 px past its current position and back. */
void menu_trigger_rubber_band_effect_46137c(bool at_top)
{
    if (g2_menu_list_obj == NULL)
        return;

    if (!at_top) {
        int32_t current = audio_uart_lv_scroll_top_44e4aa(g2_menu_list_obj);
        int32_t max_scroll = g2_menu_item_height * (g2_menu_item_count - MENU_VISIBLE_ITEMS);
        if (max_scroll < 0)
            max_scroll = 0;
        int32_t overshoot = current + MENU_RUBBER_BAND_PX;
        /* ROM 0x70cae4 / 0x6f443c */
        MENU_LOG(fn_rubber, 4u, 0x2d2u, 0x11000000u,
                 "Rubber band BOTTOM: current=%d, overshoot=%d, target=%d, max=%d",
                 current, overshoot, max_scroll, max_scroll);
        g2_lv_anim_t anim;
        audio_uart_lv_anim_init_4503d6(&anim);
        anim.var = g2_menu_list_obj;
        audio_uart_lv_anim_values_4506ce(&anim, current, overshoot);
        anim.duration = 200;
        anim.exec_cb = menu_scroll_anim_exec_cb_460fb4;
        anim.path_cb = audio_uart_lv_anim_path_450672;
        anim.reverse_duration = 200u;
        anim.reverse_delay = 0u;
        anim.completed_cb = menu_rubber_band_anim_complete_cb_461044;
        g2_menu_anim_in_progress = 1u;
        (void)audio_uart_lv_anim_start_450408(&anim);
        return;
    }

    if (g2_menu_content_container == NULL)
        return;
    int32_t y = audio_uart_lv_obj_y_43fce0(g2_menu_content_container);
    if (y != 0) {
        /* ROM 0x6fb57c / 0x6ee468 */
        MENU_LOG(fn_rubber, 2u, 0x2b2u, 0x08400000u,
                 "Content container Y not zero before rubber band: %d, resetting first", y);
        audio_uart_page_43f142(g2_menu_content_container, 0);
    }
    /* ROM 0x70caa4 / 0x6f43f0 */
    MENU_LOG(fn_rubber, 4u, 0x2bau, 0x10800000u,
             "Rubber band TOP: normal_y=%d, stretch_y=%d (content_container)", 0, MENU_RUBBER_BAND_PX);
    g2_lv_anim_t anim;
    audio_uart_lv_anim_init_4503d6(&anim);
    anim.var = g2_menu_content_container;
    audio_uart_lv_anim_values_4506ce(&anim, 0, MENU_RUBBER_BAND_PX);
    anim.duration = 200;
    anim.exec_cb = menu_rubber_band_anim_exec_cb_461374;
    anim.path_cb = audio_uart_lv_anim_path_450672;
    anim.reverse_duration = 200u;
    anim.reverse_delay = 0u;
    anim.completed_cb = menu_rubber_band_anim_complete_cb_461044;
    g2_menu_anim_in_progress = 1u;
    (void)audio_uart_lv_anim_start_450408(&anim);
}
