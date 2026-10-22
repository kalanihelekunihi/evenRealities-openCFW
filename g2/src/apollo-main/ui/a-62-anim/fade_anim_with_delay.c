/* common_fade_in_animation_with_delay, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\fade_anim.c.
 * Native 0x58c328..0x58c425; literal pool 0x58c738..0x58c75f (shared with
 * the other fade_anim.c functions at 0x58c238 and 0x58c426).
 *
 * Opacity 0 -> 255 over duration ms (default 250) after delay ms; ready_cb
 * (when non-NULL) runs on completion. The lv_anim_t lives on the stack and
 * is copied by lv_anim_start. */
#include <stdint.h>

/* Word offsets used in the stock lv_anim_t (0x60 bytes). */
enum {
    ANIM_VAR = 0x00u,
    ANIM_EXEC_CB = 0x04u,
    ANIM_COMPLETED_CB = 0x10u,
    ANIM_PATH_CB = 0x20u,
    ANIM_DURATION = 0x30u,
    ANIM_ACT_TIME = 0x34u, /* negative = start delay */
    ANIM_SIZE = 0x60u,
};

extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);   /* lv_anim_delete(var, exec_cb) */
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_legal_regulatory_fade_callback_58c12c(void);       /* opacity exec callback */
extern void audio_uart_lv_anim_path_45065a(void);                    /* lv_anim path callback (fade-in curve) */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "fade.anim"; /* ROM 0x78aa60 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\fade_anim.c"; /* ROM 0x70bf64 */
static const char fn_name[] = "common_fade_in_animation_with_delay"; /* ROM 0x7548fc */
static const char obj_invalid[] = "obj is not valid"; /* ROM 0x77f568 */
static const char obj_invalid_c[] = "[fade.anim]obj is not valid"; /* ROM 0x76b960 */
static const char started[] = "fade in animation started"; /* ROM 0x76b97c */
static const char started_c[] = "[fade.anim]fade in animation started"; /* ROM 0x74a244 */

static void anim_word(uint8_t *anim, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(anim + offset) = value;
}

void common_fade_in_animation_with_delay_58c328(void *obj, uint32_t duration, uint32_t delay, void (*ready_cb)(void *))
{
    if (obj == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_name, 0x9fu, obj_invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, obj_invalid_c, obj_invalid_c);
        return;
    }
    (void)audio_uart_lv_style_unlink_450500(obj, (void *)(uintptr_t)audio_legal_regulatory_fade_callback_58c12c);
    if (duration == 0u)
        duration = 0xfau;

    uint8_t anim[ANIM_SIZE] __attribute__((aligned(4)));
    audio_uart_lv_anim_init_4503d6(anim);
    anim_word(anim, ANIM_VAR, (uint32_t)(uintptr_t)obj);
    audio_uart_lv_anim_values_4506ce(anim, 0, 0xff);
    anim_word(anim, ANIM_DURATION, duration);
    anim_word(anim, ANIM_ACT_TIME, (uint32_t)-(int32_t)delay);
    anim_word(anim, ANIM_EXEC_CB, (uint32_t)(uintptr_t)audio_legal_regulatory_fade_callback_58c12c);
    anim_word(anim, ANIM_PATH_CB, (uint32_t)(uintptr_t)audio_uart_lv_anim_path_45065a);
    if (ready_cb != 0)
        anim_word(anim, ANIM_COMPLETED_CB, (uint32_t)(uintptr_t)ready_cb);
    (void)audio_uart_lv_anim_start_450408(anim);

    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module_tag, source_file, fn_name, 0xb1u, started);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10000000u, started_c, started_c);
}
