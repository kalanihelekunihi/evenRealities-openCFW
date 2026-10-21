/* Apollo LV draw-task style builder, native 0x452616..0x452c??.
 * Uses the verified style accessors and color helpers for each task section. */
#include <stdint.h>

#define METRIC(address) \
    extern uint32_t audio_uart_lv_draw_metric_##address(void *, uint32_t)
METRIC(4522e8); METRIC(452308); METRIC(452314); METRIC(452334);
METRIC(452340); METRIC(45234a); METRIC(452354); METRIC(452360);
METRIC(45236c); METRIC(452376); METRIC(452380); METRIC(45238c);
METRIC(4523ac); METRIC(4523b8); METRIC(4523ce); METRIC(4523ee);
METRIC(4523fa); METRIC(452404); METRIC(45241a); METRIC(452478);
METRIC(452592); METRIC(4525be); METRIC(4525f4);
#define STYLE(address) audio_uart_lv_draw_metric_##address(object, selector)

#define COMPASS(address) \
    extern uint32_t audio_uart_lv_compass_part_##address(void *, uint32_t)
COMPASS(452410); COMPASS(45243a); COMPASS(452446); COMPASS(452450);
COMPASS(45245a); COMPASS(452464); COMPASS(45246e); COMPASS(452498);
#define PART(address) audio_uart_lv_compass_part_##address(object, selector)

extern uint32_t audio_uart_lv_draw_task_opacity_452df0(void *, uint32_t, const void *);
extern uint32_t audio_uart_lv_draw_rgb_mix_452e22(void *, uint32_t, const void *, uint32_t);
extern uint32_t audio_uart_lv_draw_color_variant_452e68(void *, uint32_t,
                                                         const void *, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_image_source_type_488cb8(const void *);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void put32(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4u; ++i) p[i] = (uint8_t)(value >> (i * 8u));
}

static void color3(uint8_t *destination, uint32_t color) {
    audio_queue_copy_bytes(destination, &color, 3u);
}

void audio_uart_lv_draw_task_build_452616(void *object, uint32_t selector,
                                           void *task) {
    uint8_t *p = (uint8_t *)task;
    put32(p, (uint32_t)(uintptr_t)object);
    put32(p + 4u, selector);
    uint8_t opacity = (uint8_t)audio_uart_lv_draw_task_opacity_452df0(object, selector, task);
    if (selector != 0u && opacity <= 2u) {
        p[0x20] = p[0x3b] = p[0x48] = p[0x58] = p[0x6c] = 0u;
        return;
    }

    put32(p + 0x1cu, STYLE(4525f4));
    if (p[0x20] != 0u) {
        p[0x20] = (uint8_t)STYLE(452308);
        if (p[0x20] > 2u) {
            color3(p + 0x21u, audio_uart_lv_draw_rgb_mix_452e22(object, selector, task,
                                                                   STYLE(4522e8)));
            uint32_t border = STYLE(45236c);
            if (border != 0u &&
                ((*(const uint8_t *)(uintptr_t)(border + 0x0bu) & 0x0fu) != 0u)) {
                audio_uart_lv_grid_copy_454738(p + 0x24u,
                                                (const void *)(uintptr_t)border, 0x0cu);
            } else {
                p[0x2f] = (uint8_t)((p[0x2f] & 0xf0u) | ((uint8_t)STYLE(452334) & 0x0fu));
                if ((p[0x2f] & 0x0fu) != 0u) {
                    audio_queue_copy_bytes(p + 0x24u, p + 0x21u, 3u);
                    color3(p + 0x29u, audio_uart_lv_draw_rgb_mix_452e22(object, selector,
                                                                           task, STYLE(452314)));
                    p[0x28] = (uint8_t)STYLE(452340);
                    p[0x2d] = (uint8_t)STYLE(45234a);
                    p[0x27] = (uint8_t)STYLE(452354);
                    p[0x2c] = (uint8_t)STYLE(452360);
                }
            }
        }
    }

    if (p[0x48] != 0u) {
        put32(p + 0x44u, STYLE(4523fa));
        if (get32(p + 0x44u) != 0u) {
            p[0x48] = (uint8_t)STYLE(4523ee);
            if (p[0x48] > 2u) {
                p[0x49] = (uint8_t)((p[0x49] & 0xe0u) | ((uint8_t)STYLE(452404) & 0x1fu));
                color3(p + 0x3eu, audio_uart_lv_draw_rgb_mix_452e22(object, selector,
                                                                       task, STYLE(4523ce)));
            }
        }
    }

    if (p[0x58] != 0u) {
        put32(p + 0x50u, PART(452410));
        if (get32(p + 0x50u) != 0u) {
            p[0x58] = (uint8_t)PART(45243a);
            if (p[0x58] > 2u) {
                put32(p + 0x54u, PART(452446));
                color3(p + 0x4au, audio_uart_lv_draw_rgb_mix_452e22(object, selector,
                                                                       task, STYLE(45241a)));
            }
        }
    }

    if (p[0x3b] != 0u) {
        put32(p + 0x30u, STYLE(452376));
        if (get32(p + 0x30u) != 0u) {
            p[0x3b] = (uint8_t)STYLE(452380);
            if (p[0x3b] > 2u) {
                uint32_t kind = audio_uart_lv_image_source_type_488cb8(
                    (const void *)(uintptr_t)get32(p + 0x30u));
                if (kind == 2u) {
                    put32(p + 0x34u, STYLE(4525be));
                    color3(p + 0x38u, audio_uart_lv_draw_rgb_mix_452e22(object, selector,
                                                                           task, STYLE(452592)));
                } else {
                    uint32_t fallback = STYLE(45238c);
                    uint8_t fallback_alpha = (uint8_t)STYLE(4523ac);
                    uint32_t color = audio_uart_lv_draw_color_variant_452e68(
                        object, selector, task, fallback, fallback_alpha);
                    p[0x3c] = (uint8_t)(color >> 24u);
                    color3(p + 0x38u, color);
                    p[0x3d] = (uint8_t)STYLE(4523b8);
                }
            }
        }
    }

    if (p[0x6c] != 0u) {
        put32(p + 0x5cu, PART(452450));
        if (get32(p + 0x5cu) != 0u && p[0x6c] > 2u) {
            p[0x6c] = (uint8_t)PART(452498);
            if (p[0x6c] > 2u) {
                put32(p + 0x60u, PART(45245a));
                put32(p + 0x64u, PART(452464));
                put32(p + 0x68u, PART(45246e));
                color3(p + 0x59u, audio_uart_lv_draw_rgb_mix_452e22(object, selector,
                                                                       task, STYLE(452478)));
            }
        }
    }

    if (opacity < 0xfdu) {
        static const uint8_t offsets[] = {0x20u, 0x3bu, 0x48u, 0x6cu, 0x58u};
        for (unsigned i = 0; i < sizeof(offsets); ++i)
            p[offsets[i]] = (uint8_t)(((uint32_t)opacity * p[offsets[i]]) >> 8u);
    }
}
