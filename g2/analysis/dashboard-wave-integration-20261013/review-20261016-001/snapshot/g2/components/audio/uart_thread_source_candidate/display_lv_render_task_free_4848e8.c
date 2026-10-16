/* Apollo LV render-task cleanup and image descriptor selection. */
#include <stdint.h>

extern uint32_t audio_uart_lv_area_height_4515a4(const void *area);
extern void audio_uart_font_bitmap_release(void *buffer);
extern void audio_uart_lv_heap_free(void *pointer);
extern void audio_uart_lvgl_log(uint32_t level, const char *source, uint32_t line,
                                const char *format, ...);

void *audio_uart_lv_draw_task_image_desc_489fc8(void *task) {
    uint8_t *t = (uint8_t *)task;
    return t[4] == 5u ? (void *)(uintptr_t)*(uint32_t *)(void *)(t + 0x54u) : (void *)0;
}

void audio_uart_lv_render_task_free_4848e8(void *task, void *display) {
    uint8_t *t = (uint8_t *)task;
    if (t[4] == 7u) {
        uint8_t *descriptor = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(t + 0x54u);
        uint8_t *cell = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(descriptor + 0x1cu);
        uint32_t buffer = *(uint32_t *)(void *)cell;
        if (buffer != 0u) {
            uint32_t height = audio_uart_lv_area_height_4515a4(cell + 4u);
            uint32_t width = *(uint32_t *)(uintptr_t)(buffer + 8u) & 0xffffu;
            uint32_t used = width * height;
            volatile uint32_t *account = (volatile uint32_t *)(uintptr_t)0x2006f68cu;
            if (*account < used) {
                *account = 0u;
                audio_uart_lvgl_log(2u, (const char *)(uintptr_t)0x6e859cu, 0x230u,
                                    (const char *)(uintptr_t)0x786640u,
                                    (const char *)(uintptr_t)0x74a834u);
            } else {
                *account -= used;
            }
            audio_uart_font_bitmap_release((void *)(uintptr_t)buffer);
            *(uint32_t *)(void *)cell = 0u;
        }
        if (display != (void *)0) {
            uint8_t *d = (uint8_t *)display;
            for (uint32_t node = *(uint32_t *)(void *)(d + 0x2acu);
                 node != 0u;
                 node = *(uint32_t *)(uintptr_t)(node + 0x4cu)) {
                if (*(uint32_t *)(uintptr_t)(node + 0x4cu) == (uint32_t)(uintptr_t)cell) {
                    *(uint32_t *)(uintptr_t)(node + 0x4cu) =
                        *(uint32_t *)(void *)(cell + 0x4cu);
                    break;
                }
            }
            uint32_t callback = *(uint32_t *)(void *)(d + 0x2b4u);
            if (callback != 0u)
                ((void (*)(void *, void *))(uintptr_t)callback)(display, cell);
            audio_uart_lv_heap_free(cell);
        }
    }
    uint8_t *image = (uint8_t *)audio_uart_lv_draw_task_image_desc_489fc8(task);
    if (image != (void *)0 && (image[0x54u] & 1u) != 0u) {
        audio_uart_lv_heap_free((void *)(uintptr_t)*(uint32_t *)(void *)(image + 0x1cu));
        *(uint32_t *)(void *)(image + 0x1cu) = 0u;
    }
    audio_uart_lv_heap_free((void *)(uintptr_t)*(uint32_t *)(void *)(t + 0x54u));
    audio_uart_lv_heap_free(task);
}
