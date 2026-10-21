/* Apollo Main expand animation and four update callbacks, 0x5b7684..0x5b7901. */
#include <stdint.h>

extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43f0e0(uint32_t, int32_t);
extern void audio_uart_page_43f142(uint32_t, int32_t);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450672(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "expand.anim";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\anim\\expand_anim.c";
static const char function[] = "expand_animation_play";
static const char invalid[] = "expand_animation_play: obj is invalid";
static const char invalid_compact[] =
    "[expand.anim]expand_animation_play: obj is invalid";
static const char missing[] = "expand_animation_play: cfg is NULL";
static const char missing_compact[] =
    "[expand.anim]expand_animation_play: cfg is NULL";

uint32_t audio_conversate_expand_width_5b7684(
    uint32_t object, uint32_t value, uint32_t arg2, uint32_t passthrough) {
    (void)arg2;
    if (object != 0u && audio_terminal_ui_object_valid_43e2ea(
            (void *)(uintptr_t)object) != 0u)
        audio_uart_page_43f506(object, value);
    return passthrough;
}

uint32_t audio_conversate_expand_height_5b76a4(
    uint32_t object, uint32_t value, uint32_t arg2, uint32_t passthrough) {
    (void)arg2;
    if (object != 0u && audio_terminal_ui_object_valid_43e2ea(
            (void *)(uintptr_t)object) != 0u)
        audio_uart_page_43f568(object, value);
    return passthrough;
}

uint32_t audio_conversate_expand_x_5b76c4(
    uint32_t object, uint32_t value, uint32_t arg2, uint32_t passthrough) {
    (void)arg2;
    if (object != 0u && audio_terminal_ui_object_valid_43e2ea(
            (void *)(uintptr_t)object) != 0u)
        audio_uart_page_43f0e0(object, (int32_t)value);
    return passthrough;
}

uint32_t audio_conversate_expand_y_5b76e4(
    uint32_t object, uint32_t value, uint32_t arg2, uint32_t passthrough) {
    (void)arg2;
    if (object != 0u && audio_terminal_ui_object_valid_43e2ea(
            (void *)(uintptr_t)object) != 0u)
        audio_uart_page_43f142(object, (int32_t)value);
    return passthrough;
}

static uint16_t half(const uint8_t *bytes, uint32_t offset) {
    return (uint16_t)((uint16_t)bytes[offset] |
                      ((uint16_t)bytes[offset + 1u] << 8u));
}

static uint32_t word(const uint8_t *bytes, uint32_t offset) {
    return (uint32_t)bytes[offset] | ((uint32_t)bytes[offset + 1u] << 8u) |
        ((uint32_t)bytes[offset + 2u] << 16u) |
        ((uint32_t)bytes[offset + 3u] << 24u);
}

typedef uint32_t (*update_fn)(uint32_t, uint32_t, uint32_t, uint32_t);

void audio_conversate_expand_animation_5b7704(
    uint32_t object, const void *configuration, void (*complete)(void)) {
    if (object == 0u || audio_terminal_ui_object_valid_43e2ea(
            (void *)(uintptr_t)object) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x2fu, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_compact,
                                        invalid_compact);
        return;
    }
    if (configuration == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x33u, missing);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, missing_compact,
                                        missing_compact);
        return;
    }
    const update_fn updates[4] = {
        audio_conversate_expand_width_5b7684,
        audio_conversate_expand_height_5b76a4,
        audio_conversate_expand_x_5b76c4,
        audio_conversate_expand_y_5b76e4,
    };
    for (uint32_t i = 0; i < 4u; ++i)
        (void)audio_uart_lv_style_unlink_450500(
            (void *)(uintptr_t)object, (void *)(uintptr_t)updates[i]);
    const uint8_t *const cfg = (const uint8_t *)configuration;
    audio_uart_page_43f09a(object, word(cfg, 4u), word(cfg, 12u));
    audio_uart_page_43f4c0(object, word(cfg, 20u), word(cfg, 28u));
    const uint32_t duration = half(cfg, 0u) == 0u ? 250u : half(cfg, 0u);
    for (uint32_t i = 0; i < 4u; ++i) {
        uint32_t animation[24];
        audio_uart_lv_anim_init_4503d6(animation);
        animation[0] = object;
        audio_uart_lv_anim_values_4506ce(animation,
                                        (int32_t)word(cfg, 4u + i * 8u),
                                        (int32_t)word(cfg, 8u + i * 8u));
        animation[12] = duration;
        animation[1] = (uint32_t)(uintptr_t)updates[i == 0u ? 2u :
                                                       i == 1u ? 3u :
                                                       i == 2u ? 0u : 1u];
        animation[8] = (uint32_t)(uintptr_t)audio_uart_lv_anim_path_450672;
        animation[13] = 0u - (uint32_t)half(cfg, 2u);
        if (i == 3u && complete != 0)
            animation[4] = (uint32_t)(uintptr_t)complete;
        (void)audio_uart_lv_anim_start_450408(animation);
    }
}
