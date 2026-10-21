/* LVGL 9.3 image scheduler, stock Apollo Main 0x488a38..0x488cb7.
 * Layout and branches are grounded in the pinned payload and upstream lv_draw_image.c. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_image_header_488f6a(const void *, void *);
extern uint32_t audio_uart_lv_image_decoder_open_488f9c(void *, const void *, const void *);
extern void *audio_uart_lv_render_task_alloc_4843ee(void *, const void *);
extern uint32_t audio_uart_lv_render_task_queue_484476(void *, void *, uint32_t);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_ambiq_transform_area_488cda(void *, int32_t, int32_t,
                                                     int32_t, int32_t, int32_t,
                                                     const void *);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *, const void *,
                                                     const void *);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_image.c";
static const char source_func[] = "lv_draw_image";
static const char null_src[] = "Image draw: src is NULL";
static const char info_failed[] = "Couldn't get info about the image";
static const char open_failed[] = "Failed to open image";
static const char alloc_failed[] = "Out of memory";
static const char alloc_assert[] = "new_image_dsc != NULL";
static const char assert_format[] = "Asserted at expression: %s (%s)";

static uint32_t rd(const uint8_t *p, uint32_t offset) {
    return *(const uint32_t *)(const void *)(p + offset);
}
static void wr(uint8_t *p, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(p + offset) = value;
}
static void cp16(void *dst, const void *src) {
    (void)audio_uart_display_area_copy_439c04(dst, src, 16u);
}
static void xform(uint8_t *area, const uint8_t *dsc, const uint8_t *coords) {
    const int32_t height = audio_uart_lv_area_height_4515a4(coords);
    const int32_t width = audio_uart_lv_area_width_451598(coords);
    audio_uart_ambiq_transform_area_488cda(
        area, width, height,
        (int32_t)rd(dsc, 0x30u), (int32_t)(uint16_t)rd(dsc, 0x34u),
        (int32_t)(uint16_t)rd(dsc, 0x38u), dsc + 0x44u);
    audio_uart_ambiq_area_move_450bb2(area, (int32_t)rd(coords, 0u),
                                        (int32_t)rd(coords, 4u));
}

void audio_uart_lv_draw_image_488a38(void *layer_arg, const void *dsc_arg,
                                      const void *coords_arg) {
    uint8_t *layer = (uint8_t *)layer_arg;
    const uint8_t *dsc = (const uint8_t *)dsc_arg;
    const uint8_t *coords = (const uint8_t *)coords_arg;
    if (rd(dsc, 0x1cu) == 0u) {
        audio_uart_lvgl_log(2u, source_path, 0x69u, source_func, null_src);
        return;
    }
    if (dsc[0x50u] <= 2u || (int32_t)rd(dsc, 0x34u) < 1 ||
        (int32_t)rd(dsc, 0x38u) < 1)
        return;

    uint8_t *task_dsc = (uint8_t *)audio_uart_lv_malloc(0x6cu);
    if (task_dsc == 0) {
        audio_uart_lvgl_log(3u, source_path, 0x76u, source_func,
                            assert_format, alloc_assert, alloc_failed);
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
        for (;;) { }
    }
    (void)audio_uart_lv_grid_copy_454738(task_dsc, dsc, 0x6cu);
    if (audio_uart_lv_image_header_488f6a((const void *)(uintptr_t)rd(task_dsc, 0x1cu),
                                         task_dsc + 0x20u) != 1u) {
        audio_uart_lvgl_log(2u, source_path, 0x7au, source_func, info_failed);
        audio_uart_lv_heap_free(task_dsc);
        return;
    }
    if (rd(task_dsc, 0x60u) == 0xe0000001u)
        cp16(task_dsc + 0x58u, coords);
    if ((rd(task_dsc, 0x20u) & 0x00400000u) == 0u) {
        uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, coords);
        wr(task, 0x54u, (uint32_t)(uintptr_t)task_dsc);
        task[4u] = 6u;
        xform(task + 0x18u, dsc, coords);
        (void)audio_uart_lv_render_task_queue_484476(layer, task, 0u);
        return;
    }

    uint8_t decoder[0x4cu];
    if (audio_uart_lv_image_decoder_open_488f9c(decoder,
            (const void *)(uintptr_t)rd(task_dsc, 0x1cu), 0) != 1u) {
        audio_uart_lvgl_log(3u, source_path, 0x97u, source_func, open_failed);
        return;
    }
    uint32_t decoder_ptr = rd(decoder, 0u);
    uint32_t callback_ptr = decoder_ptr ? rd((const uint8_t *)(uintptr_t)decoder_ptr, 0x10u) : 0u;
    if (callback_ptr != 0u) {
        uint32_t draw_area[4], image_area[4], object_area[4], clip_area[4];
        cp16(draw_area, layer + 4u);
        cp16(image_area, coords);
        cp16(object_area, (const void *)(uintptr_t)(rd(dsc, 0u) + 0x14u));
        typedef void (*callback_t)(void *, const void *, const void *, const void *, const void *);
        callback_t callback = (callback_t)(uintptr_t)callback_ptr;
        if (rd(layer, 0x48u) != 0u) {
            if (audio_uart_lv_area_intersect_450bcc(image_area, image_area,
                                                      object_area) != 0u) {
                audio_uart_ambiq_area_move_450bb2(image_area,
                    -(int32_t)draw_area[0], -(int32_t)draw_area[1]);
                cp16(layer + 0x18u, image_area);
                callback(layer, decoder, image_area, task_dsc, image_area);
            }
        } else {
            cp16(clip_area, draw_area);
            if (audio_uart_lv_area_intersect_450bcc(clip_area, clip_area,
                                                      image_area) != 0u) {
                xform((uint8_t *)image_area, dsc, coords);
                xform((uint8_t *)clip_area, dsc, coords);
                if (audio_uart_lv_area_intersect_450bcc(clip_area, clip_area,
                                                          object_area) != 0u)
                    callback(layer, decoder, image_area, task_dsc, clip_area);
            }
        }
    }
    audio_uart_lv_heap_free(task_dsc);
}
