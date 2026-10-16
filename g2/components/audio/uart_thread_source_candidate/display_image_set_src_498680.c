/* Apollo LVGL image source setter 0x498680..0x4988d5.
 * Flow follows pinned LVGL v9.3 lv_image_set_src; field offsets follow native
 * load/store sites. Logging and assertion failure paths remain oracle gates. */
#include <stdint.h>

extern void audio_uart_display_size_changed(void *); /* 0x440656 */
extern uint32_t audio_uart_lv_image_source_type_488cb8(const void *);
extern uint32_t audio_uart_lv_image_header_488f6a(const void *, void *);
extern void audio_uart_lv_heap_free(void *); /* 0x44f758 */
extern char *audio_uart_font_path_duplicate(const char *); /* 0x4547c6 */
extern const void *audio_uart_lv_image_text_font_498640(void *, uint32_t);
extern int32_t audio_uart_lv_image_letter_space_49864a(void *, uint32_t);
extern int32_t audio_uart_lv_image_line_space_498654(void *, uint32_t);
extern void audio_uart_page_event_calculate_489546(void *, const char *,
    const void *, int32_t, int32_t, int32_t, uint32_t);
extern void audio_uart_page_relayout_43ffa0(void *); /* 0x43ffa0 */
extern void audio_uart_lv_image_update_align_4992cc(void *);
extern void audio_uart_lv_refresh_draw_452d42(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);
extern int32_t audio_uart_lv_snprintf_483fd0(char *, uint32_t, const char *, ...);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\image\\lv_image.c";
static const char function[] = "lv_image_set_src";

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_page_498680(void *object, const void *source) {
    if (object == 0) {
        audio_uart_lvgl_log(3u, source_path, 0x96u, function,
            "Asserted at expression: %s (%s)", "obj != NULL", "NULL pointer");
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    uint8_t *image = (uint8_t *)object;
    audio_uart_display_size_changed(object);
    uint32_t type = (uint8_t)audio_uart_lv_image_source_type_488cb8(source);
    uint32_t old_type = get32(image + 0x58u) & 3u;
    if (type == 3u) {
        if (source != 0)
            audio_uart_lvgl_log(2u, source_path, 0xafu, function,
                "unknown image type");
        if (old_type == 1u || old_type == 2u)
            audio_uart_lv_heap_free((void *)(uintptr_t)get32(image + 0x2cu));
        put32(image + 0x2cu, 0u);
        put32(image + 0x58u, get32(image + 0x58u) | 3u);
        return;
    }

    uint32_t header[2] = {0u, 0u};
    if ((uint8_t)audio_uart_lv_image_header_488f6a(source, header) != 1u) {
        char formatted[24];
        const char *description = (const char *)source;
        if (type != 1u) {
            (void)audio_uart_lv_snprintf_483fd0(formatted, sizeof(formatted),
                                                  "%p", source);
            description = formatted;
        }
        audio_uart_lvgl_log(2u, source_path, 0xbeu, function,
            "failed to get image info: %s", description);
        return;
    }
    if (type == 0u) {
        /* Header flags are at bits 16..31; ALLOCATED is bit 4. */
        if ((header[0] & 0x00100000u) != 0u) {
            const uint8_t *draw_buffer = (const uint8_t *)source;
            if (get32(draw_buffer + 20u) == 0u ||
                get32(draw_buffer + 24u) == 0u) {
                audio_uart_lvgl_log(3u, source_path, 0xc9u, function,
                    "Invalid draw buffer, unaligned_data: %p, handlers: %p",
                    (void *)(uintptr_t)get32(draw_buffer + 20u),
                    (void *)(uintptr_t)get32(draw_buffer + 24u));
                return;
            }
        }
        if (old_type == 1u || old_type == 2u)
            audio_uart_lv_heap_free((void *)(uintptr_t)get32(image + 0x2cu));
        put32(image + 0x2cu, (uint32_t)(uintptr_t)source);
    }
    else if (type == 1u || type == 2u) {
        if (get32(image + 0x2cu) != (uint32_t)(uintptr_t)source) {
            uint32_t old_source = (old_type == 1u || old_type == 2u) ?
                get32(image + 0x2cu) : 0u;
            char *copy = audio_uart_font_path_duplicate((const char *)source);
            if (copy == 0) {
                audio_uart_lvgl_log(3u, source_path, 0xdfu, function,
                    "Asserted at expression: %s (%s)", "new_str != NULL",
                    "Out of memory");
                for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
            }
            put32(image + 0x2cu, (uint32_t)(uintptr_t)copy);
            if (old_source != 0u)
                audio_uart_lv_heap_free((void *)(uintptr_t)old_source);
        }
    }
    if (type == 2u) {
        uint32_t size[2];
        audio_uart_page_event_calculate_489546(size, (const char *)source,
            audio_uart_lv_image_text_font_498640(object, 0u),
            audio_uart_lv_image_letter_space_49864a(object, 0u),
            audio_uart_lv_image_line_space_498654(object, 0u),
            0x1fffffffu, 0u);
        header[1] = ((size[1] & 0xffffu) << 16u) | (size[0] & 0xffffu);
    }
    uint32_t state = get32(image + 0x58u);
    state = (state & ~3u) | type;
    put32(image + 0x58u, state);
    put32(image + 0x3cu, header[1] & 0xffffu);
    put32(image + 0x40u, header[1] >> 16u);
    state = get32(image + 0x58u);
    state = (state & ~(0x1fu << 2u)) | (((header[0] >> 8u) & 0x1fu) << 2u);
    put32(image + 0x58u, state);
    (void)audio_uart_page_relayout_43ffa0(object);
    audio_uart_lv_image_update_align_4992cc(object);
    if (get32(image + 0x44u) != 0u || get32(image + 0x48u) != 256u ||
        get32(image + 0x4cu) != 256u)
        audio_uart_lv_refresh_draw_452d42(object);
    audio_uart_display_size_changed(object);
}
