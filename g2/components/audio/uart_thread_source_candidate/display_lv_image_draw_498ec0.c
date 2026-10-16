/* Stock LVGL 9.3 image draw helper, 0x498ec0..0x4991bf.
 * Branches follow the authenticated Apollo image and lv_image.c upstream. */
#include <stdint.h>

extern uint32_t audio_uart_page_event_code_450286(const void *);
extern uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t);
extern uint32_t audio_uart_lv_image_style_opa_498634(void *, uint32_t);
extern uint32_t audio_uart_lv_area_contains_450f28(const void *, const void *,
                                                    uint32_t);
extern void audio_uart_lv_image_get_pivot_498b82(void *, void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_ambiq_transform_area_488cda(void *, int32_t, int32_t,
                                                     int32_t, int32_t, int32_t,
                                                     const void *);
extern void *audio_uart_lv_event_layer_451960(void *);
extern void audio_uart_ambiq_image_options_init_488918(void *);
extern void audio_uart_lv_obj_init_draw_image_452a34(void *, uint32_t, void *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_image_style_radius_49865e(void *, uint32_t);
extern void audio_uart_lv_area_set_450b5c(void *, int32_t, int32_t, int32_t,
                                           int32_t);
extern void audio_uart_lv_area_transform_451082(const void *, void *, uint32_t,
                                                 uint32_t, uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(void *, const void *,
                                                     const void *);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern void audio_uart_lv_draw_image_488a38(void *, const void *, const void *);
extern void audio_uart_lv_image_descriptor_init_489f5e(void *);
extern void audio_uart_lv_draw_label_dsc_init_452988(void *, uint32_t, void *);
extern void audio_uart_lv_draw_label_489fe0(void *, const void *, const void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\image\\lv_image.c";
static const char function[] = "draw_image";
static const char null_source[] = "image source is NULL";
static const char invalid_source[] = "image source type is unknown";

static uint32_t word(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void put(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

static void copy16(void *destination, const void *source) {
    (void)audio_uart_display_area_copy_439c04(destination, source, 16u);
}

static void image_cover_check(uint8_t *image, uint8_t *info) {
    if (info[0] == 2u)
        return;
    const uint32_t state = word(image, 0x58u);
    const uint32_t kind = state & 3u;
    if (kind == 2u || kind == 3u ||
        audio_uart_lv_color_has_alpha_440fc4((state >> 2u) & 0x1fu) != 0u ||
        (uint8_t)audio_uart_lv_image_style_opa_498634(image, 0u) != 0xffu ||
        word(image, 0x44u) != 0u) {
        info[0] = 1u;
        return;
    }
    const void *area = (const void *)(uintptr_t)word(info, 4u);
    if (word(image, 0x48u) == 0x100u && word(image, 0x4cu) == 0x100u) {
        if (audio_uart_lv_area_contains_450f28(area, image + 0x14u, 0u) == 0u) {
            info[0] = 1u;
            return;
        }
    } else {
        int32_t pivot[2];
        int32_t transformed[4];
        audio_uart_lv_image_get_pivot_498b82(image, pivot);
        const int32_t height = audio_uart_lv_obj_height_43fdda(image);
        const int32_t width = audio_uart_lv_obj_width_43fd9e(image);
        audio_uart_ambiq_transform_area_488cda(
            transformed, width, height, 0,
            (int32_t)(uint16_t)word(image, 0x48u),
            (int32_t)(uint16_t)word(image, 0x4cu), pivot);
        const int32_t x = (int32_t)word(image, 0x14u);
        const int32_t y = (int32_t)word(image, 0x18u);
        transformed[0] += x; transformed[1] += y;
        transformed[2] += x; transformed[3] += y;
        if (audio_uart_lv_area_contains_450f28(area, transformed, 0u) == 0u) {
            info[0] = 1u;
            return;
        }
    }
    if (word(image, 0x30u) != 0u)
        info[0] = 1u;
}

static void draw_main(uint8_t *event, uint8_t *image) {
    const int32_t width = (int32_t)word(image, 0x3cu);
    const int32_t height = (int32_t)word(image, 0x40u);
    if (width == 0 || height == 0 || word(image, 0x48u) == 0u ||
        word(image, 0x4cu) == 0u)
        return;
    uint8_t *layer = (uint8_t *)audio_uart_lv_event_layer_451960(event);
    const uint32_t kind = word(image, 0x58u) & 3u;
    if (kind == 0u || kind == 1u) {
        uint32_t frame_words[0x114u / 4u];
        uint8_t *frame = (uint8_t *)frame_words;
        uint8_t *descriptor = frame + 0x44u;
        uint8_t *backup = frame + 0x34u;
        uint8_t *coords = frame + 0x24u;
        uint8_t *image_area = frame + 0x9cu;
        uint8_t *layer_clip = layer + 0x18u;
        audio_uart_ambiq_image_options_init_488918(descriptor);
        put(frame, 0x54u, (uint32_t)(uintptr_t)layer);
        audio_uart_lv_obj_init_draw_image_452a34(image, 0u, descriptor);
        copy16(backup, layer_clip);
        audio_uart_lv_image_get_pivot_498b82(image, frame + 0x88u);
        put(frame, 0x78u, word(image, 0x48u));
        put(frame, 0x7cu, word(image, 0x4cu));
        put(frame, 0x74u, word(image, 0x44u));
        const uint32_t flags = word(image, 0x58u);
        uint16_t bits = *(uint16_t *)(void *)(frame + 0x94u);
        bits = (uint16_t)((bits & ~0x800u) | (((flags >> 7u) & 1u) << 11u));
        bits = (uint16_t)((bits & ~0x700u) | (((flags >> 12u) & 7u) << 8u));
        *(uint16_t *)(void *)(frame + 0x94u) = bits;
        put(frame, 0xacu, word(image, 0x30u));
        put(frame, 0x60u, word(image, 0x2cu));
        const int32_t x = (int32_t)word(image, 0x14u);
        const int32_t y = (int32_t)word(image, 0x18u);
        audio_uart_lv_area_set_450b5c(image_area, x, y, x + width - 1,
                                       y + height - 1);
        put(frame, 0x70u, audio_uart_lv_image_style_radius_49865e(image, 0u));
        const uint32_t align = (flags >> 8u) & 0xfu;
        if (align < 10u) {
            audio_uart_lv_area_transform_451082(image + 0x14u, image_area,
                                                 align, word(image, 0x34u),
                                                 word(image, 0x38u));
            copy16(coords, image_area);
        } else if (align == 12u) {
            (void)audio_uart_lv_area_intersect_450bcc(layer_clip, layer_clip,
                                                       image + 0x14u);
            audio_uart_ambiq_area_move_450bb2(image_area,
                (int32_t)word(image, 0x34u), (int32_t)word(image, 0x38u));
            const int32_t dx = (((int32_t)word(layer_clip, 0u) -
                (int32_t)word(image_area, 0u) - (width - 1)) / width) * width;
            const int32_t dy = (((int32_t)word(layer_clip, 4u) -
                (int32_t)word(image_area, 4u) - (height - 1)) / height) * height;
            audio_uart_ambiq_area_move_450bb2(image_area, dx, dy);
            copy16(coords, layer_clip);
            *(uint16_t *)(void *)(frame + 0x94u) |= 0x1000u;
        } else {
            copy16(coords, image_area);
        }
        audio_uart_lv_draw_image_488a38(layer, descriptor, coords);
        copy16(layer_clip, backup);
    } else if (kind == 2u) {
        uint32_t frame_words[0x114u / 4u];
        uint8_t *frame = (uint8_t *)frame_words;
        uint8_t *descriptor = frame + 0xb0u;
        audio_uart_lv_image_descriptor_init_489f5e(descriptor);
        put(frame, 0xc0u, (uint32_t)(uintptr_t)layer);
        audio_uart_lv_draw_label_dsc_init_452988(image, 0u, descriptor);
        put(frame, 0xccu, word(image, 0x2cu));
        audio_uart_lv_draw_label_489fe0(layer, descriptor, image + 0x14u);
    } else if (word(image, 0x2cu) == 0u) {
        audio_uart_lvgl_log(2u, path, 0x339u, function, null_source);
    } else {
        audio_uart_lvgl_log(2u, path, 0x33du, function, invalid_source);
    }
}

void audio_uart_lv_image_draw_498ec0(void *event) {
    uint8_t *ev = (uint8_t *)event;
    const uint32_t code = audio_uart_page_event_code_450286(event);
    uint8_t *image = (uint8_t *)(uintptr_t)word(ev, 0u);
    if (code == 0x1au) {
        image_cover_check(image,
            (uint8_t *)(uintptr_t)word(ev, 0x10u));
    } else if (code == 0x1du) {
        draw_main(ev, image);
    }
}
