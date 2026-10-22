/* Buzzer driver, stock D:\01_workspace\s200_ap510b_iar_git\driver\buzzer\drv_buzzer.c.
 * Native 0x5026bc..0x502d55 (DRV_BuzzerPlay 0x502bf0 lives in
 * drivers/peripherals/wear-child as audio_wear_child_502bf0); float constant
 * 0x5029f8, literal pool 0x502ca8..0x502d4b.
 *
 * The buzzer is driven by Apollo510 TIMER7 in PWM mode (function 4) on
 * GPIO 145, timer output 14 (TIMER7 OUT0). The timer clock is 96 MHz divided
 * by 4 << (2 * clock_select); DRV_BuzzerInit picks clock 0 (24 MHz), 1 kHz,
 * 30 % duty. compare0 is the period, compare1 the inverted duty point.
 *
 * Voice scripts: byte 0 repeat count, byte 1 repeat interval in 10 ms units,
 * then (note, tone, beat) triples ended by note 0. note 1..7 with tone 0..3
 * picks a reload value from two 28-entry tables (frequency =
 * 1e6 / (0xffff - reload)); note >= 8 is a rest. Each step lasts beat * 62
 * ticks. Steps are paced by the one-shot "buzzer_timer", whose callback only
 * posts input-thread message 2; the input thread then calls buzzer_play_next.
 *
 * Uses single-precision FP: build with profile g2-apollo-main-3. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "g2_buzzer.h"

#define BUZZER_TIMER        7u
#define BUZZER_GPIO         145u
#define BUZZER_TIMER_FN_PWM 4u
#define BUZZER_TIMER_HZ     96000000u
#define BUZZER_VOICE_COUNT  9
#define BUZZER_VOICE_STRIDE 50u
#define BUZZER_STEP_TICKS   62u

/* am_hal_timer_config_t as used by the stock HAL (24 bytes; only the input
 * clock at +0 and the function at +2 are set here). */
typedef struct {
    uint16_t input_clock; /* +0x00 */
    uint8_t function;     /* +0x02 */
    uint8_t rest[21];     /* +0x03 filled by am_hal_timer_default_config_set */
} g2_am_timer_config_t;
_Static_assert(sizeof(g2_am_timer_config_t) == 24, "stock timer config is 24 bytes");

/* osTimerAttr_t at ROM 0x785c60. */
typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
} g2_os_timer_attr_t;

extern uint64_t g2_buzzer_timer_clock_hz;      /* RAM 0x20074120 */
extern uint8_t g2_buzzer_note_script[8];       /* RAM 0x20074128 */
extern const uint8_t *g2_buzzer_voice;         /* RAM 0x20074500, current step list */
extern void *g2_buzzer_timer;                  /* RAM 0x20074504 osTimerId_t */
extern uint8_t g2_buzzer_timer_control_block[44]; /* RAM 0x200735f8 */
extern uint16_t g2_buzzer_interval_ms;         /* RAM 0x20074f2e */
extern uint8_t g2_buzzer_repeat_count;         /* RAM 0x20074fb4 */
extern uint8_t g2_buzzer_step_index;           /* RAM 0x20074fb5 */
extern const uint32_t g2_buzzer_pwm_pin_config; /* RAM 0x20000724, GPIO 145 timer-output pad */
extern const uint32_t g2_audio_clock_pin_config; /* ROM 0x78ee48, disabled pad */
extern const uint8_t g2_buzzer_reload_high[28]; /* ROM 0x76b014 */
extern const uint8_t g2_buzzer_reload_low[28];  /* ROM 0x76b030 */
extern const uint8_t g2_buzzer_voices[BUZZER_VOICE_COUNT][BUZZER_VOICE_STRIDE]; /* ROM 0x6c1e2c */

extern uint32_t am_hal_timer_default_config_set_471cae(g2_am_timer_config_t *config);
extern uint32_t am_hal_timer_config_471c9a(uint32_t timer, g2_am_timer_config_t *config);
extern uint32_t am_hal_timer_start_471cd6(uint32_t timer);
extern uint32_t am_hal_timer_stop_471d58(uint32_t timer);
extern uint32_t am_hal_timer_clear_stop_471dac(uint32_t timer);
extern uint32_t am_hal_timer_output_config_471e20(uint32_t pin, uint32_t output);
extern uint32_t am_hal_timer_compare0_set_471e5e(uint32_t timer, uint32_t value);
extern uint32_t am_hal_timer_compare1_set_471e78(uint32_t timer, uint32_t value);
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);
extern void *osTimerNew(void (*func)(void *), uint32_t type, void *argument, const void *attr);
extern int32_t osTimerStart(void *timer, uint32_t ticks);
extern int32_t osTimerStop(void *timer);
extern void input_msg_send_id1(void);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "drv.buzzer"; /* ROM 0x78a8c8 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\buzzer\\drv_buzzer.c"; /* ROM 0x70ae24 */
static const char fn_play_voice[] = "_buzzerPlayVoice"; /* ROM 0x77ef50 */
static const char fn_play_start[] = "_buzzerPlayStart"; /* ROM 0x77ef64 */
static const char fn_init[] = "DRV_BuzzerInit"; /* ROM 0x785c50 */
static const char fn_after_queue[] = "DRV_BuzzerPlayAfterQueue"; /* ROM 0x76aff8 */
static const char fn_play_note[] = "DRV_BuzzerPlayNote"; /* ROM 0x77ef8c */
static const char timer_name[] = "buzzer_timer"; /* ROM 0x785c40 */
static const char s_again[] = "play again times=%d, intervel=%d"; /* ROM 0x753a14 */
static const char c_again[] = "[drv.buzzer]play again times=%d, intervel=%d"; /* ROM 0x733494 */
static const char s_stop[] = "beep:stop"; /* ROM 0x78a8d4 */
static const char c_stop[] = "[drv.buzzer]beep:stop"; /* ROM 0x776c04 */
static const char s_beep[] = "beep: freq=%d, delay=%d times=%d"; /* ROM 0x753a38 */
static const char c_beep[] = "[drv.buzzer]beep: freq=%d, delay=%d times=%d"; /* ROM 0x7334c4 */
static const char s_null_voice[] = "_buzzerPlayStart: pVoice=NULL"; /* ROM 0x75f6d0 */
static const char c_null_voice[] = "[drv.buzzer]_buzzerPlayStart: pVoice=NULL"; /* ROM 0x73e1e8 */
static const char s_start[] = "_buzzerPlayStart: times=%d, interval=%d"; /* ROM 0x74954c */
static const char c_start[] = "[drv.buzzer]_buzzerPlayStart: times=%d, interval=%d"; /* ROM 0x728c34 */
static const char s_timer_fail[] = "[buzzerPwmGpioInit]osTimerNew failed"; /* ROM 0x749574 */
static const char c_timer_fail[] = "[drv.buzzer][buzzerPwmGpioInit]osTimerNew failed"; /* ROM 0x728c68 */
static const char s_type_range[] = "DRV_BuzzerPlayAfterQueue type out of range"; /* ROM 0x73e214 */
static const char c_type_range[] = "[drv.buzzer]DRV_BuzzerPlayAfterQueue type out of range"; /* ROM 0x71e140 */
static const char s_play_type[] = "buzzer play type %d"; /* ROM 0x77ef78 */
static const char c_play_type[] = "[drv.buzzer]buzzer play type %d"; /* ROM 0x75f6f0 */
static const char s_note[] = "DRV_BuzzerPlayNote note=%d, tone=%d, beat=%d"; /* ROM 0x7334f4 */
static const char c_note[] = "[drv.buzzer]DRV_BuzzerPlayNote note=%d, tone=%d, beat=%d"; /* ROM 0x7145a8 */

static const g2_os_timer_attr_t buzzer_timer_attr = { /* ROM 0x785c60 */
    timer_name, 0u, g2_buzzer_timer_control_block, sizeof(g2_buzzer_timer_control_block)};

#define BUZZER_LOG_ON()  (audio_log_flags() & 2u)
#define BUZZER_CLOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

uint32_t buzzer_pwm_config(uint32_t timer, uint16_t clock, uint32_t frequency, uint8_t duty) {
    g2_am_timer_config_t config;
    (void)am_hal_timer_default_config_set_471cae(&config);
    config.function = BUZZER_TIMER_FN_PWM;
    config.input_clock = clock;
    (void)am_hal_timer_config_471c9a(timer, &config);
    (void)am_hal_timer_output_config_471e20(BUZZER_GPIO, timer << 1);
    int32_t divider = 4 << ((uint32_t)config.input_clock << 1);
    g2_buzzer_timer_clock_hz = (uint64_t)BUZZER_TIMER_HZ / (uint64_t)(int64_t)divider;
    uint64_t period = (g2_buzzer_timer_clock_hz + (frequency >> 1)) / frequency;
    (void)am_hal_timer_compare0_set_471e5e(timer, (uint32_t)period);
    /* duty is the high share in percent; compare1 marks the low part. */
    uint32_t low = (uint32_t)((float)period * (1.0f - (float)duty / 100.0f) + 0.5f);
    (void)am_hal_timer_compare1_set_471e78(timer, low);
    return 0u;
}

void buzzer_pwm_start(void) {
    (void)am_hal_timer_start_471cd6(BUZZER_TIMER);
    (void)am_hal_timer_start_471cd6(BUZZER_TIMER);
}

void buzzer_pwm_stop(void) {
    (void)am_hal_timer_clear_stop_471dac(BUZZER_TIMER);
    (void)am_hal_timer_stop_471d58(BUZZER_TIMER);
}

void buzzer_pwm_update(uint32_t frequency, uint8_t duty) {
    uint64_t period = (g2_buzzer_timer_clock_hz + (frequency >> 1)) / frequency;
    uint32_t low = (uint32_t)((float)period * (1.0f - (float)duty / 100.0f) + 0.5f);
    (void)am_hal_timer_compare0_set_471e5e(BUZZER_TIMER, (uint32_t)period);
    (void)am_hal_timer_compare1_set_471e78(BUZZER_TIMER, low);
}

void buzzer_beep_start(uint32_t frequency, uint8_t duty) {
    buzzer_pwm_update(frequency, duty);
    buzzer_pwm_start();
}

/* release parks GPIO 145 as a disabled pad. */
void buzzer_beep_stop(uint8_t release) {
    buzzer_pwm_stop();
    if (release != 0u)
        (void)am_hal_gpio_pinconfig_480f0c(BUZZER_GPIO, g2_audio_clock_pin_config);
}

/* One script step per timer expiry. At the terminator the script restarts
 * after the repeat interval until the repeat count is used up. */
void _buzzerPlayVoice(void) {
    if (g2_buzzer_voice == NULL || g2_buzzer_voice[g2_buzzer_step_index] == 0u) {
        g2_buzzer_step_index = 0u;
        if (g2_buzzer_voice != NULL) {
            g2_buzzer_repeat_count = (uint8_t)(g2_buzzer_repeat_count - 1u);
            if (g2_buzzer_repeat_count != 0u) {
                buzzer_beep_stop(0u);
                if (BUZZER_LOG_ON())
                    audio_log_extended(4u, module_tag, source_file, fn_play_voice, 0xddu, s_again,
                                       g2_buzzer_repeat_count, g2_buzzer_interval_ms);
                if (BUZZER_CLOG_ON())
                    (void)compress_log_output(0x10800000u, c_again, c_again,
                                              g2_buzzer_repeat_count, g2_buzzer_interval_ms);
                (void)osTimerStart(g2_buzzer_timer, g2_buzzer_interval_ms);
                return;
            }
        }
        buzzer_beep_stop(1u);
        g2_buzzer_voice = NULL;
        if (BUZZER_LOG_ON())
            audio_log_extended(4u, module_tag, source_file, fn_play_voice, 0xe3u, s_stop);
        if (BUZZER_CLOG_ON())
            (void)compress_log_output(0x10000000u, c_stop, c_stop);
        return;
    }

    int32_t frequency;
    const uint8_t *step = &g2_buzzer_voice[g2_buzzer_step_index];
    if ((int32_t)step[0] < 8) {
        int32_t index = (int32_t)step[1] * 7 + (int32_t)step[0] - 1;
        frequency = 1000000 / (int32_t)(0xffffu - (((uint32_t)g2_buzzer_reload_high[index] << 8) |
                                                   g2_buzzer_reload_low[index]));
    } else {
        frequency = 0;
    }
    uint16_t delay = (uint16_t)(g2_buzzer_voice[g2_buzzer_step_index + 2u] * BUZZER_STEP_TICKS);
    g2_buzzer_step_index = (uint8_t)(g2_buzzer_step_index + 3u);
    if (BUZZER_LOG_ON())
        audio_log_extended(4u, module_tag, source_file, fn_play_voice, 0xf3u, s_beep,
                           frequency, (uint32_t)delay, g2_buzzer_repeat_count);
    if (BUZZER_CLOG_ON())
        (void)compress_log_output(0x10c00000u, c_beep, c_beep, frequency, (uint32_t)delay,
                                  g2_buzzer_repeat_count);
    if (frequency == 0)
        buzzer_beep_stop(0u);
    else
        buzzer_beep_start((uint32_t)frequency, 30u);
    (void)osTimerStart(g2_buzzer_timer, delay);
}

void buzzer_timer_callback(void *argument) {
    (void)argument;
    input_msg_send_id1();
}

void _buzzerPlayStart(const uint8_t *voice) {
    if (voice == NULL) {
        if (BUZZER_LOG_ON())
            audio_log_extended(2u, module_tag, source_file, fn_play_start, 0x10bu, s_null_voice);
        if (BUZZER_CLOG_ON())
            (void)compress_log_output(0x08000000u, c_null_voice, c_null_voice);
        return;
    }
    if (BUZZER_LOG_ON())
        audio_log_extended(4u, module_tag, source_file, fn_play_start, 0x10fu, s_start, voice[0], voice[1]);
    if (BUZZER_CLOG_ON())
        (void)compress_log_output(0x10800000u, c_start, c_start, voice[0], voice[1]);
    g2_buzzer_step_index = 0u;
    g2_buzzer_repeat_count = voice[0];
    g2_buzzer_interval_ms = (uint16_t)(voice[1] * 10u);
    g2_buzzer_voice = voice + 2;
    (void)am_hal_gpio_pinconfig_480f0c(BUZZER_GPIO, g2_buzzer_pwm_pin_config);
    (void)osTimerStart(g2_buzzer_timer, 1u);
}

void _buzzerPlayStop(void) {
    (void)osTimerStop(g2_buzzer_timer);
    buzzer_beep_stop(1u);
    g2_buzzer_voice = NULL;
    g2_buzzer_step_index = 0u;
    g2_buzzer_repeat_count = 0u;
}

void DRV_BuzzerInit(void) {
    (void)buzzer_pwm_config(BUZZER_TIMER, 0u, 1000u, 30u);
    g2_buzzer_timer = osTimerNew(buzzer_timer_callback, 0u /* osTimerOnce */, NULL, &buzzer_timer_attr);
    if (g2_buzzer_timer == NULL) {
        if (BUZZER_LOG_ON())
            audio_log_extended(1u, module_tag, source_file, fn_init, 300u, s_timer_fail);
        if (BUZZER_CLOG_ON())
            (void)compress_log_output(0x04000000u, c_timer_fail, c_timer_fail);
    }
}

void buzzer_play_next(void) {
    if (g2_buzzer_voice != NULL)
        _buzzerPlayVoice();
}

void DRV_BuzzerPlayAfterQueue(int32_t type) {
    if (type >= BUZZER_VOICE_COUNT) {
        if (BUZZER_LOG_ON())
            audio_log_extended(1u, module_tag, source_file, fn_after_queue, 0x13du, s_type_range);
        if (BUZZER_CLOG_ON())
            (void)compress_log_output(0x04000000u, c_type_range, c_type_range);
        return;
    }
    if (BUZZER_LOG_ON())
        audio_log_extended(3u, module_tag, source_file, fn_after_queue, 0x140u, s_play_type, type);
    if (BUZZER_CLOG_ON())
        (void)compress_log_output(0x0c400000u, c_play_type, c_play_type, type);
    _buzzerPlayStop();
    _buzzerPlayStart(&g2_buzzer_voices[0][0] + type * (int32_t)BUZZER_VOICE_STRIDE);
}

/* One-shot script {1 repeat, 0 interval, note, tone, beat, end}. */
void DRV_BuzzerPlayNote(uint8_t note, uint8_t tone, uint8_t beat) {
    if (BUZZER_LOG_ON())
        audio_log_extended(3u, module_tag, source_file, fn_play_note, 0x14cu, s_note, note, tone, beat);
    if (BUZZER_CLOG_ON())
        (void)compress_log_output(0x0cc00000u, c_note, c_note, note, tone, beat);
    uint8_t *script = g2_buzzer_note_script;
    script[0] = 1u;
    script[1] = 0u;
    script[2] = note;
    script[3] = tone;
    script[4] = beat;
    script[5] = 0u;
    script[6] = 0u;
    script[7] = 0u;
    _buzzerPlayStop();
    _buzzerPlayStart(script);
}

/* Raw tone: stop any script, route GPIO 145 to the timer, start PWM. */
void DRV_BuzzerStart(uint32_t frequency, uint8_t duty) {
    _buzzerPlayStop();
    (void)am_hal_gpio_pinconfig_480f0c(BUZZER_GPIO, g2_buzzer_pwm_pin_config);
    buzzer_beep_start(frequency, duty);
}

void DRV_BuzzerStop(void) {
    buzzer_beep_stop(1u);
}
