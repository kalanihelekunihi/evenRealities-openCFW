/* Apollo LVGL object constructor 0x44cf98..0x44d0cf.
 * Allocation size follows the class-chain lookup at native 0x44d230. */
#include <stdint.h>

extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void *audio_uart_display_default_get(void);
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern void audio_uart_lv_obj_setup_layer_43e1fa(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_class.c";

static uint32_t class_size(const void *descriptor) {
    const uint8_t *current = (const uint8_t *)descriptor;
    while (current != 0) {
        uint32_t const size = (*(const uint32_t *)(const void *)(current + 0x20u) &
                               0xfffffu) >> 4u;
        if (size != 0u)
            return size;
        current = *(const uint8_t *const *)(const void *)current;
    }
    return 0u;
}

void *audio_uart_page_create_44cf98(const void *descriptor, void *parent) {
    uint8_t *const page = (uint8_t *)audio_uart_lv_heap_alloc(class_size(descriptor));
    if (page == 0)
        return 0;
    *(const void **)(void *)page = descriptor;
    *(void **)(void *)(page + 4u) = parent;

    if (parent == 0) {
        uint8_t *const display = (uint8_t *)audio_uart_display_default_get();
        if (display == 0) {
            audio_uart_lvgl_log(2u, path, 0x3du, "lv_obj_class_create_obj",
                "No display created yet. No place to assign the new screen");
            audio_uart_lv_heap_free(page);
            return 0;
        }
        uint32_t *const count = (uint32_t *)(void *)(display + 0x2d4u);
        if (*(uint32_t *)(void *)(display + 0x2b8u) == 0u)
            *count = 0u;
        uint32_t *const screens = (uint32_t *)audio_uart_lv_realloc_44f76a(
            *(void **)(void *)(display + 0x2b8u), (*count + 1u) * 4u);
        if (screens == 0) {
            audio_uart_lvgl_log(3u, path, 0x47u, "lv_obj_class_create_obj",
                "Asserted at expression: %s (%s)", "screens != NULL", "Out of memory");
            for (;;) { }
        }
        *count += 1u;
        *(uint32_t *)(void *)(display + 0x2b8u) = (uint32_t)(uintptr_t)screens;
        screens[*count - 1u] = (uint32_t)(uintptr_t)page;
        *(uint32_t *)(void *)(page + 0x14u) = 0u;
        *(uint32_t *)(void *)(page + 0x18u) = 0u;
        *(uint32_t *)(void *)(page + 0x1cu) =
            audio_uart_lv_display_width_44fa7e(0) - 1u;
        *(uint32_t *)(void *)(page + 0x20u) =
            audio_uart_lv_display_height_44faa8(0) - 1u;
    }
    else {
        uint8_t *const p = (uint8_t *)parent;
        if (*(uint32_t *)(void *)(p + 8u) == 0u)
            audio_uart_lv_obj_setup_layer_43e1fa(parent);
        uint8_t *const layer = *(uint8_t **)(void *)(p + 8u);
        uint16_t *const count = (uint16_t *)(void *)(layer + 0x30u);
        *count = (uint16_t)(*count + 1u);
        uint32_t *const children = (uint32_t *)audio_uart_lv_realloc_44f76a(
            *(void **)(void *)layer, (uint32_t)*count << 2u);
        *(uint32_t *)(void *)layer = (uint32_t)(uintptr_t)children;
        children[(uint32_t)*count - 1u] = (uint32_t)(uintptr_t)page;
    }
    return page;
}
