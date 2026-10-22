/* EvenHub common text container: scrolling, rubber band and event injection, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_text_container.c (log tag
 * "common_text_container"). Native 0x4df97c..0x4e0b1f; literal pools 0x4e0288..0x4e033b and
 * 0x4e0b20..0x4e0c0b (shared with the create/destroy half of the file, 0x4dee64..0x4df965,
 * reconstructed in ui/a-27-evenhub-common-containers).
 *
 * Events: 0 DOWN (scroll y += step, bottom rubber band), 1 UP (y -= step, top rubber band),
 * 2 UPDATE (re-set the label from the text buffer and scroll to top). While an animation runs,
 * scroll events try to extend it and otherwise queue a 5-byte record {event, u16 a, u16 b} in
 * the ui_common_api FIFO; the animation completion callbacks replay one queued record. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define COMMON_TEXT_LEN 0x800u

typedef int32_t (*common_text_event_cb_t)(uint8_t is_top, void *user);

/* Text container handle (0x828 bytes, allocated by common_text_create 0x4dee96). */
typedef struct {
    void *scroll_container;          /* +0x000 */
    void *content_container;         /* +0x004 */
    void *text_label;                /* +0x008 */
    int32_t max_scroll_y;            /* +0x00c */
    uint8_t at_top;                  /* +0x010 */
    uint8_t at_bottom;               /* +0x011 */
    uint8_t scrollable;              /* +0x012 */
    uint8_t anim_busy;               /* +0x013 */
    void *anim_target;               /* +0x014 object of the running scroll animation */
    void *fifo;                      /* +0x018 */
    int32_t visible_height;          /* +0x01c */
    char text[COMMON_TEXT_LEN];      /* +0x020 */
    common_text_event_cb_t event_cb; /* +0x820 boundary callback (is_top, user) */
    void *user_data;                 /* +0x824 */
} common_text_t;
_Static_assert(offsetof(common_text_t, event_cb) == 0x820, "text handle");
_Static_assert(sizeof(common_text_t) == 0x828, "text handle");

/* LVGL 9.3 lv_anim_t as laid out on the stack (0x60 bytes); stock fills it with the inline
 * lv_anim_set_* helpers, i.e. plain stores. */
typedef struct g2_lv_anim {
    void *var;                                     /* +0x00 */
    void (*exec_cb)(void *var, int32_t value);     /* +0x04 */
    void *custom_exec_cb;                          /* +0x08 */
    void *start_cb;                                /* +0x0c */
    void (*completed_cb)(struct g2_lv_anim *anim); /* +0x10 */
    void *deleted_cb;                              /* +0x14 */
    void *get_value_cb;                            /* +0x18 */
    void *user_data;                               /* +0x1c */
    int32_t (*path_cb)(void *anim);                /* +0x20 */
    int32_t start_value;                           /* +0x24 */
    int32_t current_value;                         /* +0x28 */
    int32_t end_value;                             /* +0x2c */
    int32_t duration;                              /* +0x30 */
    int32_t act_time;                              /* +0x34 */
    uint32_t reverse_delay;                        /* +0x38 */
    uint32_t reverse_duration;                     /* +0x3c */
    uint8_t reserved_40[0x20];
} g2_lv_anim_t;
_Static_assert(offsetof(g2_lv_anim_t, reverse_duration) == 0x3c, "lv_anim_t");
_Static_assert(sizeof(g2_lv_anim_t) == 0x60, "lv_anim_t frame");

enum {
    COMMON_TEXT_EVENT_DOWN = 0u,
    COMMON_TEXT_EVENT_UP = 1u,
    COMMON_TEXT_EVENT_UPDATE = 2u,
};

#define LINE_STEP 28              /* scroll step granularity, px */
#define SCROLL_ANIM_MS 200
#define RUBBER_BAND_PX 16
#define RUBBER_BAND_MS 100
#define FIFO_RECORD_LEN 5u

/* LVGL (stock fork). */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);   /* lv_obj_is_valid */
extern void audio_uart_page_43f142(uint32_t obj, uint32_t y);        /* lv_obj_set_y */
extern void audio_uart_page_43f66c(void *obj);                       /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *obj);           /* lv_obj_get_scroll_top */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);        /* lv_obj_get_scroll_bottom */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(void *anim);              /* lv_anim_init */
extern void *audio_uart_lv_anim_start_450408(void *anim);            /* lv_anim_start */
extern uint32_t audio_uart_lv_style_unlink_450500(void *var, void *exec_cb); /* lv_anim_delete */
extern void *audio_uart_page_lv_anim_lookup_450566(void *var, void *exec_cb); /* lv_anim_get */
extern int32_t audio_uart_lv_anim_path_450672(void *anim);           /* lv_anim_path_ease_out */
extern void audio_uart_lv_anim_values_4506ce(void *anim, int32_t start, int32_t end);
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern uint32_t g2_log_module_length(const char *s);                 /* strlen 0x44a43c */

/* ui_common_api.c byte FIFO. */
extern int32_t ui_common_api_fn_00509ca2(void *fifo, const void *data, uint32_t len); /* push, 0 ok */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);                            /* 1 empty */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len);  /* pop, bytes */

/* First half of common_text_container.c. */
extern void common_text_update_scroll_state_4df858(common_text_t *text);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char ct_tag[] = "common_text_container"; /* ROM 0x775a7c */
static const char ct_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\common_text_container.c"; /* ROM 0x6f22fc */

static const char fn_exec[] = "common_text_scroll_anim_exec_cb"; /* ROM 0x75e790 */
static const char ex_invalid[] = "common_text_scroll_anim_exec_cb: Invalid object, animation stopped"; /* ROM 0x700da4 */
static const char ex_invalid_s[] = "[common_text_container]common_text_scroll_anim_exec_cb: Invalid object, animation stopped"; /* ROM 0x6dfb08 */

static const char fn_scroll_done[] = "common_text_scroll_anim_complete_cb"; /* ROM 0x7529c4 */
static const char sd_done[] = "common_text_scroll_anim_complete_cb: scroll animation complete"; /* ROM 0x709e24 */
static const char sd_done_s[] = "[common_text_container]common_text_scroll_anim_complete_cb: scroll animation complete"; /* ROM 0x6e29b8 */
static const char sd_cached[] = "common_text_scroll_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6f9014 */
static const char sd_cached_s[] = "[common_text_container]common_text_scroll_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6dce74 */
static const char sd_reinject[] = "common_text_scroll_anim_complete_cb: re-injecting event %d"; /* ROM 0x7131f8 */
static const char sd_reinject_s[] = "[common_text_container]common_text_scroll_anim_complete_cb: re-injecting event %d"; /* ROM 0x6e6cac */

static const char fn_scroll[] = "common_text_scroll_with_anim"; /* ROM 0x75e7b0 */
static const char sw_invalid[] = "common_text_scroll_with_anim: scroll_container is invalid"; /* ROM 0x713234 */
static const char sw_invalid_s[] = "[common_text_container]common_text_scroll_with_anim: scroll_container is invalid"; /* ROM 0x6e6d00 */
static const char sw_started[] = "common_text_scroll_with_anim: Started scroll animation from %d to %d over %d ms"; /* ROM 0x6ec1b8 */
static const char sw_started_s[] = "[common_text_container]common_text_scroll_with_anim: Started scroll animation from %d to %d over %d ms"; /* ROM 0x6d87fc */

static const char fn_rubber_done[] = "common_text_rubber_band_anim_complete_cb"; /* ROM 0x73cb0c */
static const char rb_done[] = "common_text_rubber_band_anim_complete_cb: rubber band animation complete"; /* ROM 0x6f242c */
static const char rb_done_s[] = "[common_text_container]common_text_rubber_band_anim_complete_cb: rubber band animation complete"; /* ROM 0x6dced4 */
static const char rb_reset[] = "Resetting content_container Y from %d to 0"; /* ROM 0x73cb38 */
static const char rb_reset_s[] = "[common_text_container]Resetting content_container Y from %d to 0"; /* ROM 0x700de8 */
static const char rb_cached[] = "common_text_rubber_band_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6f2478 */
static const char rb_cached_s[] = "[common_text_container]common_text_rubber_band_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6da3b8 */
static const char rb_reinject[] = "common_text_rubber_band_anim_complete_cb: re-injecting event %d"; /* ROM 0x709e64 */
static const char rb_reinject_s[] = "[common_text_container]common_text_rubber_band_anim_complete_cb: re-injecting event %d"; /* ROM 0x6e2a10 */

static const char fn_trigger[] = "common_text_trigger_rubber_band"; /* ROM 0x75e7d0 */
static const char tr_not_zero[] = "Content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6f905c */
static const char tr_not_zero_s[] = "[common_text_container]Content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6dfb64 */
static const char tr_top[] = "Triggering TOP rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x71cc78 */
static const char tr_top_s[] = "[common_text_container]Triggering TOP rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x6ec208 */
static const char tr_bottom[] = "Triggering BOTTOM rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x713270 */
static const char tr_bottom_s[] = "[common_text_container]Triggering BOTTOM rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x6ec258 */

static const char fn_extend[] = "common_text_try_extend_animation"; /* ROM 0x7529e8 */
static const char te_invalid[] = "common_text_try_extend_animation: Invalid scroll object"; /* ROM 0x71ccb0 */
static const char te_invalid_s[] = "[common_text_container]common_text_try_extend_animation: Invalid scroll object"; /* ROM 0x6ec2a8 */
static const char te_no_anim[] = "common_text_try_extend_animation: Failed to get animation object"; /* ROM 0x700e2c */
static const char te_no_anim_s[] = "[common_text_container]common_text_try_extend_animation: Failed to get animation object"; /* ROM 0x6e2a68 */
static const char te_state[] = "common_text_try_extend_animation: event_type=%d, original_target=%d, max_scroll=%d, dist_to_bottom=%d, dist_to_top=%d"; /* ROM 0x6d6038 */
static const char te_state_s[] = "[common_text_container]common_text_try_extend_animation: event_type=%d, original_target=%d, max_scroll=%d, dist_to_bottom=%d, dist_to_top=%d"; /* ROM 0x6d3b40 */
static const char te_bottom[] = "common_text_try_extend_animation: Will reach bottom, return false"; /* ROM 0x700e70 */
static const char te_bottom_s[] = "[common_text_container]common_text_try_extend_animation: Will reach bottom, return false"; /* ROM 0x6dfbc0 */
static const char te_top[] = "common_text_try_extend_animation: Will reach top, return false"; /* ROM 0x709ea4 */
static const char te_top_s[] = "[common_text_container]common_text_try_extend_animation: Will reach top, return false"; /* ROM 0x6e2ac0 */
static const char te_extend[] = "common_text_try_extend_animation: Extend animation: %d \xe2\x86\x92 %d (delta=%d)"; /* ROM 0x6f24c4 */
static const char te_extend_s[] = "[common_text_container]common_text_try_extend_animation: Extend animation: %d \xe2\x86\x92 %d (delta=%d)"; /* ROM 0x6dcf34 */

static const char fn_inject[] = "common_text_inject_event"; /* ROM 0x76a118 */
static const char ie_null[] = "common_text_inject_event: handle is NULL"; /* ROM 0x73cb64 */
static const char ie_null_s[] = "[common_text_container]common_text_inject_event: handle is NULL"; /* ROM 0x709ee4 */
static const char ie_not_init[] = "common_text_inject_event: text not initialized"; /* ROM 0x732114 */
static const char ie_not_init_s[] = "[common_text_container]common_text_inject_event: text not initialized"; /* ROM 0x6f90a4 */
static const char ie_unknown[] = "common_text_inject_event: unknown event type %d"; /* ROM 0x732144 */
static const char ie_unknown_s[] = "[common_text_container]common_text_inject_event: unknown event type %d"; /* ROM 0x6f90ec */
static const char ie_busy[] = "common_text_inject_event: animation in progress"; /* ROM 0x732174 */
static const char ie_busy_s[] = "[common_text_container]common_text_inject_event: animation in progress"; /* ROM 0x6f9134 */
static const char ie_extended[] = "common_text_inject_event: Extended animation successfully"; /* ROM 0x7132ac */
static const char ie_extended_s[] = "[common_text_container]common_text_inject_event: Extended animation successfully"; /* ROM 0x6e6d54 */
static const char ie_cannot[] = "common_text_inject_event: Cannot extend, push event to FIFO"; /* ROM 0x7132e8 */
static const char ie_cannot_s[] = "[common_text_container]common_text_inject_event: Cannot extend, push event to FIFO"; /* ROM 0x6e6da8 */
static const char ie_full[] = "common_text_inject_event: FIFO push failed (maybe full)"; /* ROM 0x71cce8 */
static const char ie_full_s[] = "[common_text_container]common_text_inject_event: FIFO push failed (maybe full)"; /* ROM 0x6ec2f8 */
static const char ie_nonscroll[] = "common_text_inject_event: Non-scroll event, push to FIFO"; /* ROM 0x713324 */
static const char ie_nonscroll_s[] = "[common_text_container]common_text_inject_event: Non-scroll event, push to FIFO"; /* ROM 0x6ec348 */
static const char ie_state[] = "common_text_inject_event: event_type=%d, scrollable=%d, at_top=%d, at_bottom=%d"; /* ROM 0x6ec398 */
static const char ie_state_s[] = "[common_text_container]common_text_inject_event: event_type=%d, scrollable=%d, at_top=%d, at_bottom=%d"; /* ROM 0x6d8864 */
static const char up_flat[] = "COMMON_TEXT_EVENT_UP: Content not scrollable, trigger rubber band"; /* ROM 0x700eb4 */
static const char up_flat_s[] = "[common_text_container]COMMON_TEXT_EVENT_UP: Content not scrollable, trigger rubber band"; /* ROM 0x6dfc1c */
static const char up_top[] = "COMMON_TEXT_EVENT_UP: At top, trigger rubber band"; /* ROM 0x7278e8 */
static const char up_top_s[] = "[common_text_container]COMMON_TEXT_EVENT_UP: At top, trigger rubber band"; /* ROM 0x6f2510 */
static const char up_scroll[] = "COMMON_TEXT_EVENT_UP: Scrolling from %d to %d"; /* ROM 0x7321a4 */
static const char up_scroll_s[] = "[common_text_container]COMMON_TEXT_EVENT_UP: Scrolling from %d to %d"; /* ROM 0x6f917c */
static const char dn_flat[] = "COMMON_TEXT_EVENT_DOWN: Content not scrollable, trigger rubber band"; /* ROM 0x700ef8 */
static const char dn_flat_s[] = "[common_text_container]COMMON_TEXT_EVENT_DOWN: Content not scrollable, trigger rubber band"; /* ROM 0x6dfc78 */
static const char dn_bottom[] = "COMMON_TEXT_EVENT_DOWN: At bottom, trigger rubber band"; /* ROM 0x71cd20 */
static const char dn_bottom_s[] = "[common_text_container]COMMON_TEXT_EVENT_DOWN: At bottom, trigger rubber band"; /* ROM 0x6ec3e8 */
static const char dn_scroll[] = "COMMON_TEXT_EVENT_DOWN: Scrolling from %d to %d"; /* ROM 0x7321d4 */
static const char dn_scroll_s[] = "[common_text_container]COMMON_TEXT_EVENT_DOWN: Scrolling from %d to %d"; /* ROM 0x6f91c4 */
static const char up_update[] = "COMMON_TEXT_EVENT_UPDATE: Updating text content"; /* ROM 0x732204 */
static const char up_update_s[] = "[common_text_container]COMMON_TEXT_EVENT_UPDATE: Updating text content"; /* ROM 0x6f920c */
static const char up_no_label[] = "COMMON_TEXT_EVENT_UPDATE: text_label is NULL"; /* ROM 0x732234 */
static const char up_no_label_s[] = "[common_text_container]COMMON_TEXT_EVENT_UPDATE: text_label is NULL"; /* ROM 0x700f3c */
static const char up_empty[] = "COMMON_TEXT_EVENT_UPDATE: text buffer is empty"; /* ROM 0x732264 */
static const char up_empty_s[] = "[common_text_container]COMMON_TEXT_EVENT_UPDATE: text buffer is empty"; /* ROM 0x6f9254 */
static const char up_done[] = "COMMON_TEXT_EVENT_UPDATE: Text updated (length=%d)"; /* ROM 0x72791c */
static const char up_done_s[] = "[common_text_container]COMMON_TEXT_EVENT_UPDATE: Text updated (length=%d)"; /* ROM 0x6f255c */
static const char up_reset[] = "COMMON_TEXT_EVENT_UPDATE: Scroll position reset to top"; /* ROM 0x71cd58 */
static const char up_reset_s[] = "[common_text_container]COMMON_TEXT_EVENT_UPDATE: Scroll position reset to top"; /* ROM 0x6ec438 */
static const char ie_unknown2[] = "common_text_inject_event: Unknown event type %d"; /* ROM 0x732294 */
static const char ie_unknown2_s[] = "[common_text_container]common_text_inject_event: Unknown event type %d"; /* ROM 0x6f929c */

/* Both sinks are tested separately and every argument is evaluated per sink, as in stock. */
#define TC_LOG(level, func, line, cflags, text, short_text, ...)                                 \
    do {                                                                                         \
        if ((audio_log_flags() & 2u) != 0u)                                                      \
            audio_log_extended((level), ct_tag, ct_file, (func), (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                    \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);      \
    } while (0)

void common_text_scroll_anim_exec_cb_4df9a2(void *obj, int32_t value);
void common_text_scroll_anim_complete_cb_4dfa2c(g2_lv_anim_t *anim);
void common_text_rubber_band_anim_exec_cb_4dfcb8(void *obj, int32_t value);
void common_text_rubber_band_anim_complete_cb_4dfcc0(g2_lv_anim_t *anim);
int32_t common_text_container_inject_event_4e033c(common_text_t *text, uint8_t event, uint32_t a,
                                                  uint32_t b);

/* Scroll distance for one input: at least one 28 px step, rounded up to whole steps and
 * doubled for fast input (speed > 100). No log strings; first-party helper. */
int32_t common_text_calc_scroll_step_4df97c(int32_t distance, int32_t speed)
{
    if (distance == 0)
        distance = 1;
    if (speed > 100)
        distance <<= 1;
    if (distance < LINE_STEP)
        return LINE_STEP;
    return ((distance + (LINE_STEP - 1)) / LINE_STEP) * LINE_STEP;
}

/* common_text_scroll_anim_exec_cb */
void common_text_scroll_anim_exec_cb_4df9a2(void *obj, int32_t value)
{
    if (obj != NULL && audio_terminal_ui_object_valid_43e2ea(obj) != 0u) {
        audio_uart_lv_scroll_to_y_44ea04(obj, value, 0u);
        return;
    }
    TC_LOG(2u, fn_exec, 0x1c7u, 0x08000000u, ex_invalid, ex_invalid_s);
}

/* common_text_scroll_anim_complete_cb */
void common_text_scroll_anim_complete_cb_4dfa2c(g2_lv_anim_t *anim)
{
    common_text_t *text = (common_text_t *)anim->user_data;
    uint8_t rec[FIFO_RECORD_LEN];

    TC_LOG(4u, fn_scroll_done, 0x1d1u, 0x10000000u, sd_done, sd_done_s);
    text->anim_busy = 0u;
    text->anim_target = NULL;
    common_text_update_scroll_state_4df858(text);
    if (ui_common_api_fn_00509dfa(text->fifo) != 0)
        return;
    TC_LOG(4u, fn_scroll_done, 0x1dcu, 0x10000000u, sd_cached, sd_cached_s);
    if (ui_common_api_fn_00509e14(text->fifo, rec, FIFO_RECORD_LEN) != (int32_t)FIFO_RECORD_LEN)
        return;
    uint8_t event = rec[0];
    uint16_t a = (uint16_t)(rec[1] | (rec[2] << 8));
    uint16_t b = (uint16_t)(rec[3] | (rec[4] << 8));
    TC_LOG(4u, fn_scroll_done, 0x1e2u, 0x10400000u, sd_reinject, sd_reinject_s, event);
    (void)common_text_container_inject_event_4e033c(text, event, a, b);
}

/* common_text_scroll_with_anim: ease-out scroll of the scroll container to target_y. */
void common_text_scroll_with_anim_4dfb78(common_text_t *text, int32_t target_y, int32_t duration)
{
    g2_lv_anim_t a;

    if (text == NULL || text->scroll_container == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(text->scroll_container) == 0u) {
        TC_LOG(2u, fn_scroll, 0x1f2u, 0x08000000u, sw_invalid, sw_invalid_s);
        return;
    }
    text->anim_target = text->scroll_container;
    text->anim_busy = 1u;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = text->scroll_container;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(text->scroll_container),
                                     target_y);
    a.duration = duration;
    a.exec_cb = common_text_scroll_anim_exec_cb_4df9a2;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.completed_cb = common_text_scroll_anim_complete_cb_4dfa2c;
    a.user_data = text;
    (void)audio_uart_lv_anim_start_450408(&a);
    TC_LOG(4u, fn_scroll, 0x206u, 0x10c00000u, sw_started, sw_started_s,
           audio_uart_lv_obj_y_44e498(text->scroll_container), target_y, duration);
}

/* Rubber band exec_cb (no inventory row): moves the content container. */
void common_text_rubber_band_anim_exec_cb_4dfcb8(void *obj, int32_t value)
{
    audio_uart_page_43f142((uint32_t)(uintptr_t)obj, (uint32_t)value);
}

/* common_text_rubber_band_anim_complete_cb */
void common_text_rubber_band_anim_complete_cb_4dfcc0(g2_lv_anim_t *anim)
{
    common_text_t *text = (common_text_t *)anim->user_data;
    uint8_t rec[FIFO_RECORD_LEN];
    int32_t y;

    TC_LOG(4u, fn_rubber_done, 0x216u, 0x10000000u, rb_done, rb_done_s);
    if (text->content_container != NULL &&
        (y = audio_uart_lv_obj_y_43fce0(text->content_container)) != 0) {
        TC_LOG(4u, fn_rubber_done, 0x21cu, 0x10400000u, rb_reset, rb_reset_s, y);
        audio_uart_page_43f142((uint32_t)(uintptr_t)text->content_container, 0u);
    }
    text->anim_busy = 0u;
    text->anim_target = NULL;
    if (ui_common_api_fn_00509dfa(text->fifo) != 0)
        return;
    TC_LOG(4u, fn_rubber_done, 0x227u, 0x10000000u, rb_cached, rb_cached_s);
    if (ui_common_api_fn_00509e14(text->fifo, rec, FIFO_RECORD_LEN) != (int32_t)FIFO_RECORD_LEN)
        return;
    uint8_t event = rec[0];
    uint16_t a = (uint16_t)(rec[1] | (rec[2] << 8));
    uint16_t b = (uint16_t)(rec[3] | (rec[4] << 8));
    TC_LOG(4u, fn_rubber_done, 0x22du, 0x10400000u, rb_reinject, rb_reinject_s, event);
    (void)common_text_container_inject_event_4e033c(text, event, a, b);
}

/* common_text_trigger_rubber_band: 16 px stretch of the content container (down for the top
 * edge, up for the bottom edge), 100 ms out and 100 ms back. */
void common_text_trigger_rubber_band_4dfe50(common_text_t *text, uint8_t is_top)
{
    g2_lv_anim_t a;
    int32_t y;
    int32_t stretch_y;

    if (text == NULL || text->scroll_container == NULL || text->content_container == NULL)
        return;
    if ((y = audio_uart_lv_obj_y_43fce0(text->content_container)) != 0) {
        TC_LOG(2u, fn_trigger, 0x23eu, 0x08400000u, tr_not_zero, tr_not_zero_s, y);
        audio_uart_page_43f142((uint32_t)(uintptr_t)text->content_container, 0u);
    }
    if (is_top == 0u) {
        stretch_y = -RUBBER_BAND_PX;
        TC_LOG(4u, fn_trigger, 0x24cu, 0x10800000u, tr_bottom, tr_bottom_s, 0, -RUBBER_BAND_PX);
    } else {
        stretch_y = RUBBER_BAND_PX;
        TC_LOG(4u, fn_trigger, 0x248u, 0x10800000u, tr_top, tr_top_s, 0, RUBBER_BAND_PX);
    }
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = text->content_container;
    audio_uart_lv_anim_values_4506ce(&a, 0, stretch_y);
    a.duration = RUBBER_BAND_MS;
    a.exec_cb = common_text_rubber_band_anim_exec_cb_4dfcb8;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.reverse_duration = RUBBER_BAND_MS;
    a.reverse_delay = 0u;
    a.completed_cb = common_text_rubber_band_anim_complete_cb_4dfcc0;
    a.user_data = text;
    (void)audio_uart_lv_anim_start_450408(&a);
    text->anim_busy = 1u;
}

/* common_text_try_extend_animation: retarget the running scroll animation by one more step.
 * Stock uses direction -1 for event 0 and +1 otherwise (opposite of the non-animated path). */
bool common_text_try_extend_animation_4dfff8(common_text_t *text, uint8_t event, uint32_t a,
                                             uint32_t b)
{
    if (text->anim_target == NULL ||
        audio_terminal_ui_object_valid_43e2ea(text->anim_target) == 0u) {
        TC_LOG(2u, fn_extend, 0x26bu, 0x08000000u, te_invalid, te_invalid_s);
        text->anim_target = NULL;
        return false;
    }
    g2_lv_anim_t *anim = (g2_lv_anim_t *)audio_uart_page_lv_anim_lookup_450566(
        text->anim_target, (void *)common_text_scroll_anim_exec_cb_4df9a2);
    if (anim == NULL) {
        TC_LOG(2u, fn_extend, 0x273u, 0x08000000u, te_no_anim, te_no_anim_s);
        return false;
    }
    int32_t original_target = anim->end_value;
    int32_t max_scroll = audio_uart_lv_scroll_bottom_44e4bc(text->anim_target) +
                         audio_uart_lv_scroll_top_44e4aa(text->anim_target);
    int32_t dist_to_bottom = max_scroll - original_target;
    int32_t dist_to_top = original_target;
    TC_LOG(4u, fn_extend, 0x282u, 0x11400000u, te_state, te_state_s, event, original_target,
           max_scroll, dist_to_bottom, dist_to_top);

    int32_t direction = (event == 0u) ? -1 : 1;
    if (direction >= 1 && dist_to_bottom < 3) {
        TC_LOG(4u, fn_extend, 0x289u, 0x10000000u, te_bottom, te_bottom_s);
        return false;
    }
    if (direction < 0 && dist_to_top < 3) {
        TC_LOG(4u, fn_extend, 0x28fu, 0x10000000u, te_top, te_top_s);
        return false;
    }
    int32_t step = common_text_calc_scroll_step_4df97c((int32_t)a, (int32_t)b);
    int32_t target = step * direction + original_target;
    if (target < 0)
        target = 0;
    else if (max_scroll < target)
        target = max_scroll;
    TC_LOG(4u, fn_extend, 0x2a1u, 0x10c00000u, te_extend, te_extend_s, original_target, target,
           step * direction);
    (void)audio_uart_lv_style_unlink_450500(text->anim_target,
                                            (void *)common_text_scroll_anim_exec_cb_4df9a2);
    common_text_scroll_with_anim_4dfb78(text, target, SCROLL_ANIM_MS);
    return true;
}

/* Queue {event, a, b} while an animation runs. */
#define TC_FIFO_PUSH(line, result)                                                             \
    do {                                                                                       \
        uint8_t rec_[FIFO_RECORD_LEN];                                                         \
        rec_[0] = event;                                                                       \
        rec_[1] = (uint8_t)a;                                                                  \
        rec_[2] = (uint8_t)(a >> 8);                                                           \
        rec_[3] = (uint8_t)b;                                                                  \
        rec_[4] = (uint8_t)(b >> 8);                                                           \
        if (ui_common_api_fn_00509ca2(text->fifo, rec_, FIFO_RECORD_LEN) == 0) {               \
            (result) = 0;                                                                      \
        } else {                                                                               \
            TC_LOG(2u, fn_inject, (line), 0x08000000u, ie_full, ie_full_s);                    \
            (result) = -1;                                                                     \
        }                                                                                      \
    } while (0)

/* common_text_inject_event. Returns 0 handled/queued, -1 error, 1 unknown event. */
int32_t common_text_container_inject_event_4e033c(common_text_t *text, uint8_t event, uint32_t a,
                                                  uint32_t b)
{
    int32_t result;

    if (text == NULL) {
        TC_LOG(1u, fn_inject, 0x2bau, 0x04000000u, ie_null, ie_null_s);
        return -1;
    }
    if (text->scroll_container == NULL || text->content_container == NULL) {
        TC_LOG(2u, fn_inject, 0x2bfu, 0x08000000u, ie_not_init, ie_not_init_s);
        return -1;
    }
    if (event != COMMON_TEXT_EVENT_DOWN && event != COMMON_TEXT_EVENT_UP &&
        event != COMMON_TEXT_EVENT_UPDATE) {
        TC_LOG(4u, fn_inject, 0x2c7u, 0x10400000u, ie_unknown, ie_unknown_s, event);
        return 1;
    }

    if (text->anim_busy != 0u) {
        TC_LOG(4u, fn_inject, 0x2cdu, 0x10000000u, ie_busy, ie_busy_s);
        if (event == COMMON_TEXT_EVENT_DOWN || event == COMMON_TEXT_EVENT_UP) {
            if (common_text_try_extend_animation_4dfff8(text, event, a, b)) {
                TC_LOG(4u, fn_inject, 0x2d2u, 0x10000000u, ie_extended, ie_extended_s);
                return 0;
            }
            TC_LOG(4u, fn_inject, 0x2d6u, 0x10000000u, ie_cannot, ie_cannot_s);
            TC_FIFO_PUSH(0x2deu, result);
            return result;
        }
        TC_LOG(4u, fn_inject, 0x2e5u, 0x10000000u, ie_nonscroll, ie_nonscroll_s);
        TC_FIFO_PUSH(0x2edu, result);
        return result;
    }

    common_text_update_scroll_state_4df858(text);
    TC_LOG(4u, fn_inject, 0x2fau, 0x11000000u, ie_state, ie_state_s, event, text->scrollable,
           text->at_top, text->at_bottom);

    if (event == COMMON_TEXT_EVENT_DOWN) {
        if (text->scrollable == 0u) {
            TC_LOG(4u, fn_inject, 0x32cu, 0x10000000u, dn_flat, dn_flat_s);
            if (text->event_cb != NULL)
                (void)text->event_cb(0u, text->user_data);
            common_text_trigger_rubber_band_4dfe50(text, 0u);
        } else if (text->at_bottom == 0u) {
            int32_t step = common_text_calc_scroll_step_4df97c((int32_t)a, (int32_t)b);
            int32_t from = audio_uart_lv_obj_y_44e498(text->scroll_container);
            int32_t to = step + from;
            if (text->max_scroll_y < to)
                to = text->max_scroll_y;
            TC_LOG(4u, fn_inject, 0x34eu, 0x10800000u, dn_scroll, dn_scroll_s, from, to);
            common_text_scroll_with_anim_4dfb78(text, to, SCROLL_ANIM_MS);
        } else {
            TC_LOG(4u, fn_inject, 0x339u, 0x10000000u, dn_bottom, dn_bottom_s);
            if (text->event_cb != NULL)
                (void)text->event_cb(0u, text->user_data);
            common_text_trigger_rubber_band_4dfe50(text, 0u);
        }
    } else if (event == COMMON_TEXT_EVENT_UPDATE) {
        TC_LOG(4u, fn_inject, 0x355u, 0x10000000u, up_update, up_update_s);
        if (text->text_label == NULL) {
            TC_LOG(1u, fn_inject, 0x358u, 0x04000000u, up_no_label, up_no_label_s);
            return -1;
        }
        if (text->text[0] == '\0') {
            TC_LOG(2u, fn_inject, 0x35eu, 0x08000000u, up_empty, up_empty_s);
            return -1;
        }
        (void)audio_uart_page_49942e(text->text_label, text->text);
        TC_LOG(4u, fn_inject, 0x364u, 0x10400000u, up_done, up_done_s,
               g2_log_module_length(text->text));
        audio_uart_page_43f66c(text->scroll_container);
        common_text_update_scroll_state_4df858(text);
        audio_uart_lv_scroll_to_y_44ea04(text->scroll_container, 0, 0u);
        TC_LOG(4u, fn_inject, 0x36eu, 0x10000000u, up_reset, up_reset_s);
    } else if (event > COMMON_TEXT_EVENT_UP) {
        TC_LOG(2u, fn_inject, 0x374u, 0x08400000u, ie_unknown2, ie_unknown2_s, event);
        return -1;
    } else if (text->scrollable == 0u) {
        TC_LOG(4u, fn_inject, 0x301u, 0x10000000u, up_flat, up_flat_s);
        if (text->event_cb != NULL)
            (void)text->event_cb(1u, text->user_data);
        common_text_trigger_rubber_band_4dfe50(text, 1u);
    } else if (text->at_top == 0u) {
        int32_t step = common_text_calc_scroll_step_4df97c((int32_t)a, (int32_t)b);
        int32_t from = audio_uart_lv_obj_y_44e498(text->scroll_container);
        int32_t to = from - step;
        if (to < 0)
            to = 0;
        TC_LOG(4u, fn_inject, 0x323u, 0x10800000u, up_scroll, up_scroll_s, from, to);
        common_text_scroll_with_anim_4dfb78(text, to, SCROLL_ANIM_MS);
    } else {
        TC_LOG(4u, fn_inject, 0x30eu, 0x10000000u, up_top, up_top_s);
        if (text->event_cb != NULL)
            (void)text->event_cb(1u, text->user_data);
        common_text_trigger_rubber_band_4dfe50(text, 1u);
    }
    return 0;
}
