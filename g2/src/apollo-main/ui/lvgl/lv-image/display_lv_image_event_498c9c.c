/* Stock LVGL 9.3 image class event, 0x498c9c..0x498eb3. The branch
 * structure is also attributable to third-party/upstream/lvgl lv_image.c. */
#include <stdint.h>

extern const uint8_t audio_uart_image_class_756108[];
extern uint32_t audio_uart_page_event_code_450286(const void *);
extern uint32_t audio_uart_lv_object_event_base_4516f8(const void *, void *);
extern void audio_uart_lv_image_get_pivot_498b82(void *, void *);
extern void audio_uart_page_498680(void *, const void *);
extern void audio_uart_lv_refresh_draw_452d42(void *);
extern void audio_uart_lv_image_update_align_4992cc(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_ambiq_transform_area_488cda(void *, int32_t, int32_t,
                                                     int32_t, int32_t, int32_t,
                                                     const void *);
extern void audio_uart_lv_get_click_area_4408b0(void *, void *);
extern uint32_t audio_uart_lv_round_corner_450dd4(const int32_t *, const void *,
                                                    uint32_t);
extern void audio_uart_lv_image_draw_498ec0(void *);

static uint32_t word(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void store_word(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

static uint32_t transformed(const uint8_t *image) {
    return word(image, 0x44u) != 0u || word(image, 0x48u) != 0x100u ||
           word(image, 0x4cu) != 0x100u;
}

static void area_for_image(uint8_t *image, int32_t area[4],
                           const int32_t pivot[2], int32_t width,
                           int32_t height) {
    audio_uart_ambiq_transform_area_488cda(
        area, width, height, (int32_t)word(image, 0x44u),
        (int32_t)(uint16_t)word(image, 0x48u),
        (int32_t)(uint16_t)word(image, 0x4cu), pivot);
}

void audio_uart_lv_image_event_498c9c(const void *klass, void *event) {
    (void)klass;
    const uint32_t code = audio_uart_page_event_code_450286(event);
    if ((uint8_t)audio_uart_lv_object_event_base_4516f8(
            audio_uart_image_class_756108, event) != 1u)
        return;
    uint8_t *ev = (uint8_t *)event;
    uint8_t *image = (uint8_t *)(uintptr_t)word(ev, 0u);
    int32_t pivot[2];
    audio_uart_lv_image_get_pivot_498b82(image, pivot);
    if (code == 0x32u) {
        if ((image[0x58u] & 3u) == 2u)
            audio_uart_page_498680(image,
                                   (const void *)(uintptr_t)word(image, 0x2cu));
        else
            audio_uart_lv_refresh_draw_452d42(image);
    } else if (code == 0x1bu) {
        if (transformed(image)) {
            int32_t *size = (int32_t *)(uintptr_t)word(ev, 0x10u);
            const int32_t width = audio_uart_lv_obj_width_43fd9e(image);
            const int32_t height = audio_uart_lv_obj_height_43fdda(image);
            int32_t area[4];
            area_for_image(image, area, pivot, width, height);
            int32_t margin = -area[0];
            if (margin > *size) *size = margin;
            margin = -area[1];
            if (margin > *size) *size = margin;
            margin = area[2] - width;
            if (margin > *size) *size = margin;
            margin = area[3] - height;
            if (margin > *size) *size = margin;
        }
    } else if (code == 0x31u) {
        if (((word(image, 0x58u) >> 8u) & 0xfu) == 0xbu) {
            audio_uart_lv_image_update_align_4992cc(image);
            if (transformed(image))
                audio_uart_lv_refresh_draw_452d42(image);
        }
    } else if (code == 0x16u) {
        uint8_t *info = (uint8_t *)(uintptr_t)word(ev, 0x10u);
        const int32_t width = audio_uart_lv_obj_width_43fd9e(image);
        uint32_t exact = (int32_t)word(image, 0x3cu) == width;
        if (exact) {
            const int32_t height = audio_uart_lv_obj_height_43fdda(image);
            exact = (int32_t)word(image, 0x40u) == height && transformed(image);
        }
        int32_t area[4];
        if (exact) {
            const int32_t current_width = audio_uart_lv_obj_width_43fd9e(image);
            const int32_t height = audio_uart_lv_obj_height_43fdda(image);
            area_for_image(image, area, pivot, current_width, height);
            const int32_t x = (int32_t)word(image, 0x14u);
            const int32_t y = (int32_t)word(image, 0x18u);
            area[0] += x; area[1] += y; area[2] += x; area[3] += y;
        } else {
            audio_uart_lv_get_click_area_4408b0(image, area);
        }
        info[4] = (uint8_t)audio_uart_lv_round_corner_450dd4(
            area, (const void *)(uintptr_t)word(info, 0u), 0u);
    } else if (code == 0x34u) {
        uint8_t *size = (uint8_t *)(uintptr_t)word(ev, 0x10u);
        store_word(size, 0u, word(image, 0x3cu));
        store_word(size, 4u, word(image, 0x40u));
    } else if (code == 0x1du || code == 0x20u || code == 0x1au) {
        audio_uart_lv_image_draw_498ec0(event);
    }
}
