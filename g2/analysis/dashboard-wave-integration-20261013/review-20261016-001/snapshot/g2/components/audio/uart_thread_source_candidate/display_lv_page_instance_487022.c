/* LV page instance/cache constructor, native 0x487022..0x487154. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void *audio_uart_display_current_44fa1a(void);
extern int32_t audio_uart_lv_display_dpi_44fbe6(void *);
extern int32_t audio_uart_lv_display_width_44fa7e(void *);
extern void audio_uart_lv_page_build_484a98(void *);
extern void *audio_uart_lv_theme_lookup_44fe7e(void *);
extern void audio_uart_lv_theme_refresh_all_44bc48(void *);
extern void audio_uart_lv_page_callback_487188(void);

static uint32_t read32(const uint8_t *base, uint32_t at) {
    return *(const uint32_t *)(const void *)(base + at);
}
static void write32(uint8_t *base, uint32_t at, uint32_t value) {
    *(uint32_t *)(void *)(base + at) = value;
}
static uint8_t *current_page(void) {
    return (uint8_t *)(uintptr_t)read32(audio_uart_display_lv_state, 0x178u);
}

uint32_t audio_uart_page_rgb_equal_44102e(uint32_t first, uint32_t second) {
    return (first & 0x00ffffffu) == (second & 0x00ffffffu);
}

uint8_t audio_uart_page_instance_ready_48716c(void) {
    uint8_t *instance = current_page();
    return instance == 0 ? 0u : instance[0x3cu];
}

void *audio_uart_page_487022(void *display, uint32_t foreground,
                             uint32_t background, uint32_t opacity,
                             const void *resource) {
    if (audio_uart_page_instance_ready_48716c() == 0u)
        write32(audio_uart_display_lv_state, 0x178u,
                (uint32_t)(uintptr_t)audio_uart_lv_heap_alloc(0x38cu));
    uint8_t *const instance = current_page();
    void *const target = display == 0 ? audio_uart_display_current_44fa1a() : display;
    const uint32_t dpi = (uint32_t)audio_uart_lv_display_dpi_44fbe6(target);
    const int32_t width = audio_uart_lv_display_width_44fa7e(target);
    const uint8_t size_class = width < 0x141 ? 3u : width < 0x2d0 ? 2u : 1u;
    if (instance[0x3cu] != 0u && read32(instance, 0x2cu) == dpi &&
        instance[0x28u] == size_class &&
        audio_uart_page_rgb_equal_44102e(read32(instance, 0x10u), foreground) != 0u &&
        audio_uart_page_rgb_equal_44102e(read32(instance, 0x13u), background) != 0u &&
        read32(instance, 0x24u) == (opacity & 0xffu) &&
        read32(instance, 0x18u) == (uint32_t)(uintptr_t)resource)
        return instance;

    instance[0x28u] = size_class;
    write32(instance, 0x2cu, dpi);
    write32(instance, 0x0cu, (uint32_t)(uintptr_t)target);
    instance[0x10u] = (uint8_t)foreground;
    instance[0x11u] = (uint8_t)(foreground >> 8);
    instance[0x12u] = (uint8_t)(foreground >> 16);
    instance[0x13u] = (uint8_t)background;
    instance[0x14u] = (uint8_t)(background >> 8);
    instance[0x15u] = (uint8_t)(background >> 16);
    write32(instance, 0x18u, (uint32_t)(uintptr_t)resource);
    write32(instance, 0x1cu, (uint32_t)(uintptr_t)resource);
    write32(instance, 0x20u, (uint32_t)(uintptr_t)resource);
    write32(instance, 0u, (uint32_t)(uintptr_t)audio_uart_lv_page_callback_487188);
    write32(instance, 0x24u, (opacity & 0xffu) != 0u ? 1u : 0u);
    audio_uart_lv_page_build_484a98(instance);
    if (display == 0 || audio_uart_lv_theme_lookup_44fe7e(display) == instance)
        audio_uart_lv_theme_refresh_all_44bc48(0);
    instance[0x3cu] = 1u;
    return instance;
}
