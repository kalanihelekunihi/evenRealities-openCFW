/* Apollo LVGL local text duplication 0x4547f2 (lv_strdup). lv_draw_label
 * 0x489fe0 is compiled from the generated pre-#8070 lv_draw_label.c
 * ({gen}/U2/lvgl-pre8070/lv_draw_label.c). */
#include <stdint.h>

extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_string_length_454768(const char *);

char *audio_uart_lv_draw_task_strdup_4547f2(const char *text) {
    uint32_t length = audio_uart_lv_string_length_454768(text);
    char *copy = (char *)audio_uart_lv_malloc(length + 1u);
    if (copy == 0) return 0;
    audio_uart_lv_grid_copy_454738(copy, text, length);
    copy[length] = '\0';
    return copy;
}

