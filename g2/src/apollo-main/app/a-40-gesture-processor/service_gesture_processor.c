/* Touch gesture processor, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\input\service_gesture_processor.c.
 * Native 0x502d56..0x50322f (0x502d56 is two bytes of alignment padding; the
 * first instruction is at 0x502d58); "%s|" literal at 0x502ef0; literal pool
 * 0x503230..0x503297.
 *
 * The input thread calls gesture_touch_event_process_502ef4 (stock
 * process_gesture_data) for every touch interrupt. It reads the 16-byte
 * PSoC 4000T report, forwards proximity changes to the wear-detect sync and
 * maps the slider bits onto input-manager events (0x4c5916):
 *   bit0 PRESS -> 0x0d    bit2 SINGLE -> SINGLE_CLICK 0 (count < 2) or DECA_CLICK 0x1010 (count >= 10)
 *   bit3 DOUBLE -> 1      bit4 LONG -> LONG_PRESS 3
 *   bit5 SLIDE_L -> DOWNROLL 5 (diffX, speed)   bit6 SLIDE_R -> UPROLL 4 (diffX, speed)
 *   bit1 RELEASE -> 0x0e (posted last)          bit7 ERROR -> touch controller reset
 * In production mode the slider is only used for the factory single-click beep. */
#include <stdint.h>
#include <stddef.h>
#include "g2_touch_cy8c4046.h"

/* PSoC 4000T event report (command 3), 16 bytes. The halfwords are copied out
 * with memcpy because the report is a byte buffer. */
enum {
    REPORT_PROX = 0,      /* proximity level, 0 = none */
    REPORT_SLIDER = 1,    /* SLIDER_EVENT_* bit mask */
    REPORT_DIFFX = 2,     /* click count for SINGLE, distance for SLIDE */
    REPORT_SPEED = 3,
    REPORT_BSLN = 4,      /* u16 */
    REPORT_RAW = 6,       /* u16 */
    REPORT_DIFF = 8,      /* u16 */
    REPORT_KV_BSLN = 10,  /* u16 */
    REPORT_SIZE = 16,
};

enum {
    SLIDER_PRESS = 0x01u,
    SLIDER_RELEASE = 0x02u,
    SLIDER_SINGLE = 0x04u,
    SLIDER_DOUBLE = 0x08u,
    SLIDER_LONG = 0x10u,
    SLIDER_SLIDE_L = 0x20u,
    SLIDER_SLIDE_R = 0x40u,
    SLIDER_ERROR = 0x80u,
};

enum {
    INPUT_SINGLE_CLICK = 0u,
    INPUT_DOUBLE_CLICK = 1u,
    INPUT_LONG_PRESS = 3u,
    INPUT_UPROLL = 4u,
    INPUT_DOWNROLL = 5u,
    INPUT_PRESS = 0x0du,
    INPUT_RELEASE = 0x0eu,
    INPUT_DECA_CLICK = 0x1010u,
};

#define WEAR_SYNC_PROXIMITY 3u /* wear-detect sync message type */
#define BUZZER_FACTORY_CLICK 3u
#define SLIDER_TEXT_SIZE 0x60

extern volatile uint8_t g2_touch_stream_enabled;   /* RAM 0x20075017 */
extern volatile uint8_t g2_touch_prox_state;       /* RAM 0x20075018 */
extern const char *const g2_touch_prox_names[];    /* RAM 0x200036ec, initialised data */
extern char g2_gesture_slider_text[SLIDER_TEXT_SIZE]; /* RAM 0x20072790 */

extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern int32_t log_snprintf_47344e(char *dst, uint32_t size, const char *format, ...); /* 0 when size >= 1024 or truncated */
extern uint32_t Thread_MsgStreamingNotifyByBle(const void *payload, uint16_t length); /* 0x475d78 */
extern int32_t wear_detect_sync_send_49eae2(uint8_t type, uint32_t value);
extern uint8_t productModeGet(void); /* 0x4abe60 */
extern uint32_t input_local_source_4c5874(void); /* 1 when device role is 1, else 0 */
extern void audio_uart_ring_touch_event_4c5916(uint16_t source, uint32_t event, uint8_t a, uint8_t b);
extern void DRV_BuzzerPlay(uint32_t type); /* 0x502bf0 */
extern void cy8c4046fni_reset_55b64a(void);                   /* GPIO 10 low 10 ms, high, 50 ms */
extern int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version); /* cmd 1 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "touch.ges"; /* ROM 0x78bf24 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\input\\service_gesture_processor.c"; /* ROM 0x6ef958 */
static const char production_fn[] = "production_test_gesture_process"; /* ROM 0x764e90 */
static const char process_fn[] = "process_gesture_data"; /* ROM 0x77b83c */
static const char single_click[] = "EVENT_SLIDER_SINGLE_CLICK"; /* ROM 0x77124c */
static const char single_click_short[] = "[touch.ges]EVENT_SLIDER_SINGLE_CLICK"; /* ROM 0x74de6c */
static const char flag_format[] = "%s|"; /* ROM 0x502ef0 */
static const char name_press[] = "SLIDER_EVENT_PRESS"; /* ROM 0x783244 */
static const char name_release[] = "SLIDER_EVENT_RELEASE"; /* ROM 0x77b7f4 */
static const char name_single[] = "SLIDER_EVENT_SINGLE"; /* ROM 0x783258 */
static const char name_double[] = "SLIDER_EVENT_DOUBLE"; /* ROM 0x78326c */
static const char name_long[] = "SLIDER_EVENT_LONG"; /* ROM 0x783280 */
static const char name_slide_l[] = "SLIDER_EVENT_SLIDE_L"; /* ROM 0x77b80c */
static const char name_slide_r[] = "SLIDER_EVENT_SLIDE_R"; /* ROM 0x77b824 */
static const char name_error[] = "SLIDER_EVENT_ERROR"; /* ROM 0x783294 */
static const char data_format[] =
    "prox:%d, bsln:%5d, kv_bsln:%5d, raw:%5d, diff:%4d, diffX:%3d, speed:%3d, slider:(0x%02x)%s"; /* ROM 0x6e17c8 */
static const char data_format_short[] =
    "[touch.ges]prox:%d, bsln:%5d, kv_bsln:%5d, raw:%5d, diff:%4d, diffX:%3d, speed:%3d, slider:(0x%02x)%s"; /* ROM 0x6d9974 */
static const char prox_format[] = "prox=%s(%u)"; /* ROM 0x78bf30 */
static const char prox_format_short[] = "[touch.ges]prox=%s(%u)"; /* ROM 0x77b854 */
static const char slider_format[] = "slider mask = 0x%02x(%s), diffX = %d, speed = %d"; /* ROM 0x72d484 */
static const char slider_format_short[] = "[touch.ges]slider mask = 0x%02x(%s), diffX = %d, speed = %d"; /* ROM 0x7185a4 */
static const char error_reset[] = "SLIDER_EVENT_ERROR: reset touch"; /* ROM 0x764eb0 */
static const char error_reset_short[] = "[touch.ges]SLIDER_EVENT_ERROR: reset touch"; /* ROM 0x743258 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* Stock production_test_gesture_process (row 0x502d56, code from 0x502d58). */
void production_test_gesture_process_502d56(uint8_t slider, uint8_t count)
{
    if ((slider & SLIDER_SINGLE) == 0u || count != 1u)
        return;
    DRV_BuzzerPlay(BUZZER_FACTORY_CLICK);
    if (LOG_EXT_ON())
        audio_log_extended(4u, module_tag, source_file, production_fn, 0x25u, single_click);
    if (LOG_CMP_ON())
        (void)compress_log_output(0x10000000u, single_click_short, single_click_short);
}

/* Last proximity level reported by the touch controller. */
uint8_t wear_detect_sensor_state_get_502dae(void)
{
    return g2_touch_prox_state;
}

const char *gesture_prox_name_502db6(uint8_t prox)
{
    return g2_touch_prox_names[prox];
}

/* Appends "<name>|" and clamps the cursor to the end of the buffer. */
static char *append_flag(char *cursor, char *end, const char *name)
{
    int32_t room = (int32_t)(end - cursor);
    int32_t n = log_snprintf_47344e(cursor, (uint32_t)room, flag_format, name);
    if (n >= 1) {
        if (n >= room)
            n = room;
        cursor += n;
    }
    return cursor;
}

/* Renders the slider mask as "NAME|NAME" into the shared 96-byte buffer. */
const char *gesture_slider_mask_string_502dc2(uint8_t slider)
{
    char *const text = g2_gesture_slider_text;
    char *const end = text + SLIDER_TEXT_SIZE;
    char *cursor = text;

    *cursor = '\0';
    if (slider & SLIDER_PRESS)
        cursor = append_flag(cursor, end, name_press);
    if (slider & SLIDER_RELEASE)
        cursor = append_flag(cursor, end, name_release);
    if (slider & SLIDER_SINGLE)
        cursor = append_flag(cursor, end, name_single);
    if (slider & SLIDER_DOUBLE)
        cursor = append_flag(cursor, end, name_double);
    if (slider & SLIDER_LONG)
        cursor = append_flag(cursor, end, name_long);
    if (slider & SLIDER_SLIDE_L)
        cursor = append_flag(cursor, end, name_slide_l);
    if (slider & SLIDER_SLIDE_R)
        cursor = append_flag(cursor, end, name_slide_r);
    if (slider & SLIDER_ERROR)
        cursor = append_flag(cursor, end, name_error);
    if (text < cursor && cursor[-1] == '|')
        cursor[-1] = '\0';
    return text;
}

static void post_input(uint32_t event, uint8_t a, uint8_t b)
{
    audio_uart_ring_touch_event_4c5916((uint16_t)input_local_source_4c5874(), event, a, b);
}

/* Stock process_gesture_data. */
void gesture_touch_event_process_502ef4(void)
{
    uint8_t report[REPORT_SIZE];
    uint16_t bsln, raw, diff, kv_bsln;

    (void)aeabi_memset_43c0e4(report, REPORT_SIZE, 0);
    DRV_TouchReadReport_55b676(report);
    if (g2_touch_stream_enabled != 0u)
        (void)Thread_MsgStreamingNotifyByBle(report, REPORT_SIZE);

    const uint8_t prox = report[REPORT_PROX];
    const uint8_t slider = report[REPORT_SLIDER];
    const uint8_t diffx = report[REPORT_DIFFX];
    const uint8_t speed = report[REPORT_SPEED];
    (void)audio_queue_copy_bytes(&bsln, &report[REPORT_BSLN], 2u);
    (void)audio_queue_copy_bytes(&raw, &report[REPORT_RAW], 2u);
    (void)audio_queue_copy_bytes(&diff, &report[REPORT_DIFF], 2u);
    (void)audio_queue_copy_bytes(&kv_bsln, &report[REPORT_KV_BSLN], 2u);

    if (LOG_EXT_ON()) {
        const char *names = gesture_slider_mask_string_502dc2(slider);
        audio_log_extended(3u, module_tag, source_file, process_fn, 0x70u, data_format, prox, bsln,
                           kv_bsln, raw, diff, diffx, speed, slider, names);
    }
    if (LOG_CMP_ON()) {
        const char *names = gesture_slider_mask_string_502dc2(slider);
        (void)compress_log_output(0x0e400000u, data_format_short, data_format_short, prox, bsln,
                                  kv_bsln, raw, diff, diffx, speed, slider, names);
    }

    if (prox != 0u) {
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, process_fn, 0x74u, prox_format,
                               gesture_prox_name_502db6(prox), prox);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c800000u, prox_format_short, prox_format_short,
                                      gesture_prox_name_502db6(prox), prox);
        g2_touch_prox_state = prox;
        (void)wear_detect_sync_send_49eae2(WEAR_SYNC_PROXIMITY, prox);
    }

    if (slider == 0u)
        return;
    if (productModeGet() == 1u) {
        production_test_gesture_process_502d56(slider, diffx);
        return;
    }

    if (LOG_EXT_ON()) {
        const char *names = gesture_slider_mask_string_502dc2(slider);
        audio_log_extended(4u, module_tag, source_file, process_fn, 0x82u, slider_format, slider,
                           names, diffx, speed);
    }
    if (LOG_CMP_ON()) {
        const char *names = gesture_slider_mask_string_502dc2(slider);
        (void)compress_log_output(0x11000000u, slider_format_short, slider_format_short, slider,
                                  names, diffx, speed);
    }

    if (slider & SLIDER_ERROR) {
        uint32_t version;
        if (LOG_EXT_ON())
            audio_log_extended(1u, module_tag, source_file, process_fn, 0x85u, error_reset);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x04000000u, error_reset_short, error_reset_short);
        cy8c4046fni_reset_55b64a();
        version = 0u;
        (void)cy8c4046fni_read_version_55b6dc(&version);
        return;
    }

    if (slider & SLIDER_PRESS)
        post_input(INPUT_PRESS, 0u, 0u);
    if (slider & SLIDER_SINGLE) {
        if (diffx < 2u)
            post_input(INPUT_SINGLE_CLICK, 0u, 0u);
        else if (diffx >= 10u)
            post_input(INPUT_DECA_CLICK, 0u, 0u);
    }
    if (slider & SLIDER_DOUBLE)
        post_input(INPUT_DOUBLE_CLICK, 0u, 0u);
    if (slider & SLIDER_LONG)
        post_input(INPUT_LONG_PRESS, 0u, 0u);
    if (slider & SLIDER_SLIDE_L)
        post_input(INPUT_DOWNROLL, diffx, speed);
    if (slider & SLIDER_SLIDE_R)
        post_input(INPUT_UPROLL, diffx, speed);
    if (slider & SLIDER_RELEASE)
        post_input(INPUT_RELEASE, 0u, 0u);
}
