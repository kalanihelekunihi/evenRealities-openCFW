/* Apollo LV draw-task renderer, native 0x451c6e..0x4522a7. */
#include <stdint.h>

extern void *audio_uart_lv_render_task_alloc_4843ee(void *layer, const void *area);
extern void *audio_uart_lv_malloc(uint32_t bytes);
extern void audio_uart_lv_render_task_queue_484476(void *layer, void *task);
extern void audio_uart_lv_draw_descriptor_init_451c3a(void *descriptor);
extern void audio_uart_ambiq_image_options_init_488918(void *descriptor);
extern void audio_uart_lv_image_descriptor_init_489f5e(void *descriptor);
extern uint32_t audio_uart_lv_image_source_type_488cb8(const void *source);
extern uint32_t audio_uart_lv_image_header_488f6a(const void *source, void *header);
extern void audio_uart_page_event_calculate_489546(void *output, const char *text,
    const void *font, int32_t letter_spacing, int32_t line_spacing, int32_t max_width,
    uint32_t flags);
extern void audio_uart_lv_area_transform_451082(const void *parent, void *area,
    uint32_t scale, uint32_t x, uint32_t y);
extern void audio_uart_lv_area_expand_450b98(void *area, int32_t x, int32_t y);
extern void audio_uart_ambiq_area_move_450bb2(void *area, int32_t x, int32_t y);
extern void audio_uart_lvgl_log(uint32_t level, const char *source, uint32_t line,
    const char *function, ...);

static uint32_t rd32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void wr32(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4u; ++i) p[i] = (uint8_t)(value >> (8u * i));
}
static void copy(uint8_t *to, const uint8_t *from, unsigned count) {
    for (unsigned i = 0; i < count; ++i) to[i] = from[i];
}
static void zero(uint8_t *to, unsigned count) {
    for (unsigned i = 0; i < count; ++i) to[i] = 0u;
}
static const char draw_rect_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_rect.c";
static const char draw_rect_function[] = "lv_draw_rect";
static const char draw_rect_assert[] = "Asserted at expression: %s (%s)";
static const char draw_rect_oom[] = "Out of memory";
static const char assert_shadow[] = "shadow_dsc != NULL";
static const char assert_background[] = "bg_dsc != NULL";
static const char assert_bg_image[] = "bg_image_dsc != NULL";
static const char assert_bg_label[] = "bg_label_dsc != NULL";
static const char assert_border[] = "border_dsc != NULL";
static const char assert_outline[] = "outline_dsc != NULL";
static uint8_t *descriptor(uint8_t *task, uint32_t bytes, uint32_t line,
                            const char *message) {
    uint8_t *d = (uint8_t *)audio_uart_lv_malloc(bytes);
    if (d == (void *)0) {
        audio_uart_lvgl_log(3u, draw_rect_source, line, draw_rect_function,
                            draw_rect_assert, message, draw_rect_oom);
        for (;;) { }
    }
    wr32(task + 0x54u, (uint32_t)(uintptr_t)d);
    return d;
}

void audio_uart_lv_draw_task_render_451c6e(void *layer, const void *options,
                                              const void *area) {
    const uint8_t *o = (const uint8_t *)options;
    const uint8_t *box = (const uint8_t *)area;
    uint32_t arc_kind = rd32(o + 0x5cu);
    uint8_t arc = arc_kind != 0u && o[0x6cu] >= 3u &&
        !(arc_kind == 1u && (int32_t)rd32(o + 0x68u) < 1 &&
          rd32(o + 0x60u) == 0u && rd32(o + 0x64u) == 0u);
    uint8_t image = o[0x3bu] >= 3u && rd32(o + 0x30u) != 0u;
    uint8_t border = o[0x48u] >= 3u && rd32(o + 0x44u) != 0u &&
        (o[0x49u] & 0x20u) == 0u && (o[0x49u] & 0x1fu) != 0u;
    uint8_t shadow = o[0x58u] >= 3u && rd32(o + 0x50u) != 0u;
    uint8_t opaque = 1u;
    if (o[0x20u] == 0xffu) {
        if ((o[0x2fu] & 0x0fu) != 0u) {
            for (unsigned i = 0; i < o[0x2eu]; ++i)
                if (o[0x27u + i * 5u] != 0xffu) { opaque = 0u; break; }
        }
    } else opaque = 0u;

    if (arc) {
        uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, area);
        uint8_t *d = descriptor(task, 0x38u, 200u, assert_shadow);
        audio_uart_lv_area_expand_450b98(task + 0x18u,
            (int32_t)rd32(o + 0x68u), (int32_t)rd32(o + 0x68u));
        audio_uart_lv_area_expand_450b98(task + 0x18u,
            (int32_t)arc_kind, (int32_t)arc_kind);
        audio_uart_ambiq_area_move_450bb2(task + 0x18u,
            (int32_t)rd32(o + 0x60u), (int32_t)rd32(o + 0x64u));
        copy(d, o, 0x1cu); wr32(d + 0x14u, 0x38u);
        wr32(d + 0x1cu, rd32(o + 0x1cu));
        copy(d + 0x20u, o + 0x59u, 3u);
        wr32(d + 0x24u, arc_kind); wr32(d + 0x28u, rd32(o + 0x68u));
        d[0x34u] = o[0x6cu];
        wr32(d + 0x2cu, rd32(o + 0x60u)); wr32(d + 0x30u, rd32(o + 0x64u));
        d[0x35u] = (uint8_t)((d[0x35u] & 0xfeu) | opaque);
        task[4] = 3u; audio_uart_lv_render_task_queue_484476(layer, task);
    }
    if (o[0x20u] > 2u) {
        uint8_t adjusted[16]; copy(adjusted, box, 16u);
        if ((int32_t)rd32(o + 0x44u) > 1 && o[0x48u] > 0xfcu &&
            rd32(o + 0x1cu) != 0u) {
            wr32(adjusted, rd32(adjusted) + ((o[0x49u] >> 2u) & 1u));
            wr32(adjusted + 4u, rd32(adjusted + 4u) + ((o[0x49u] >> 1u) & 1u));
            wr32(adjusted + 8u, rd32(adjusted + 8u) - ((o[0x49u] >> 3u) & 1u));
            wr32(adjusted + 12u, rd32(adjusted + 12u) - (o[0x49u] & 1u));
        }
        uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, adjusted);
        uint8_t *d = descriptor(task, 0x30u, 0xe8u, assert_background);
        audio_uart_lv_draw_descriptor_init_451c3a(d);
        copy(d, o, 0x1cu); wr32(d + 0x14u, 0x30u);
        wr32(d + 0x1cu, rd32(o + 0x1cu));
        copy(d + 0x21u, o + 0x21u, 3u);
        copy(d + 0x24u, o + 0x24u, 12u);
        d[0x20u] = o[0x20u];
        task[4] = 1u; audio_uart_lv_render_task_queue_484476(layer, task);
    }
    if (image) {
        const void *source = (const void *)(uintptr_t)rd32(o + 0x30u);
        uint8_t kind = (uint8_t)audio_uart_lv_image_source_type_488cb8(source);
        uint8_t valid = 1u;
        uint8_t header[12];
        if (kind == 0u || kind == 1u)
            valid = (uint8_t)audio_uart_lv_image_header_488f6a(source, header);
        else { zero(header, 12u); if (kind == 3u) valid = 0u; }
        if (valid) {
            if (kind == 0u || kind == 1u) {
                uint8_t clipped[16];
                if (o[0x3du] == 0u) {
                    zero(clipped, 16u);
                    wr32(clipped + 8u, (rd32(header + 4u) & 0xffffu) - 1u);
                    wr32(clipped + 12u, (rd32(header + 4u) >> 16u) - 1u);
                    audio_uart_lv_area_transform_451082(area, clipped, 9u, 0u, 0u);
                } else copy(clipped, box, 16u);
                uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, clipped);
                uint8_t *d = descriptor(task, 0x6cu, 0x113u, assert_bg_image);
                audio_uart_ambiq_image_options_init_488918(d);
                copy(d, o, 0x1cu); wr32(d + 0x14u, 0x6cu);
                wr32(d + 0x1cu, rd32(o + 0x30u)); d[0x50u] = o[0x3bu];
                copy(d + 0x4cu, o + 0x38u, 3u); d[0x4fu] = o[0x3cu];
                uint16_t flags = (uint16_t)d[0x50u] | ((uint16_t)d[0x51u] << 8u);
                flags = (uint16_t)((flags & 0xefffu) | ((o[0x3du] & 1u) << 12u));
                d[0x50u] = (uint8_t)flags; d[0x51u] = (uint8_t)(flags >> 8u);
                copy(d + 0x20u, header, 12u);
                wr32(d + 0x2cu, rd32(o + 0x1cu));
                copy(d + 0x58u, box, 16u);
                task[4] = 6u; audio_uart_lv_render_task_queue_484476(layer, task);
            } else {
                uint8_t dimensions[8], clipped[16];
                audio_uart_page_event_calculate_489546(dimensions,
                    (const char *)source, (const void *)(uintptr_t)rd32(o + 0x34u),
                    0, 0, 0x1fffffff, 0u);
                zero(clipped, 16u);
                wr32(clipped + 8u, rd32(dimensions) - 1u);
                wr32(clipped + 12u, rd32(dimensions + 4u) - 1u);
                audio_uart_lv_area_transform_451082(area, clipped, 9u, 0u, 0u);
                uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, clipped);
                uint8_t *d = descriptor(task, 100u, 300u, assert_bg_label);
                audio_uart_lv_image_descriptor_init_489f5e(d);
                copy(d, o, 0x1cu); wr32(d + 0x14u, 100u);
                copy(d + 0x24u, o + 0x38u, 3u);
                wr32(d + 0x20u, rd32(o + 0x34u));
                wr32(d + 0x1cu, rd32(o + 0x30u));
                task[4] = 5u; audio_uart_lv_render_task_queue_484476(layer, task);
            }
        }
    }
    if (border) {
        uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, area);
        uint8_t *d = descriptor(task, 0x2cu, 0x13eu, assert_border);
        copy(d, o, 0x1cu); wr32(d + 0x14u, 0x2cu);
        wr32(d + 0x1cu, rd32(o + 0x1cu));
        copy(d + 0x20u, o + 0x3eu, 3u);
        d[0x28u] = o[0x48u]; wr32(d + 0x24u, rd32(o + 0x44u));
        d[0x29u] = (uint8_t)((o[0x49u] & 0x1fu) | (d[0x29u] & 0xe0u));
        task[4] = 2u; audio_uart_lv_render_task_queue_484476(layer, task);
    }
    if (shadow) {
        uint8_t adjusted[16]; copy(adjusted, box, 16u);
        int32_t radius = (int32_t)(rd32(o + 0x54u) + rd32(o + 0x50u));
        audio_uart_lv_area_expand_450b98(adjusted, radius, radius);
        uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, adjusted);
        uint8_t *d = descriptor(task, 0x2cu, 0x151u, assert_outline);
        audio_uart_lv_area_expand_450b98(task + 0x18u,
            (int32_t)rd32(o + 0x50u), (int32_t)rd32(o + 0x50u));
        audio_uart_lv_area_expand_450b98(task + 0x18u,
            (int32_t)rd32(o + 0x54u), (int32_t)rd32(o + 0x54u));
        copy(d, o, 0x1cu); wr32(d + 0x14u, 0x2cu);
        wr32(d + 0x1cu, rd32(o + 0x1cu) == 0x7fffu ? 0x7fffu :
            rd32(o + 0x54u) + rd32(o + 0x50u) + rd32(o + 0x1cu));
        copy(d + 0x20u, o + 0x4au, 3u);
        d[0x28u] = o[0x58u]; wr32(d + 0x24u, rd32(o + 0x50u));
        d[0x29u] = (uint8_t)((d[0x29u] & 0xe0u) | 0x0fu);
        task[4] = 2u; audio_uart_lv_render_task_queue_484476(layer, task);
    }
}
