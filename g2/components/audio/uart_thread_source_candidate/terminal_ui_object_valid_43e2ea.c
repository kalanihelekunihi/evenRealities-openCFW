/* Stock LVGL object membership check 0x43e2ea. */
#include <stdint.h>

extern void *audio_uart_lv_display_next_44fa22(void *);
extern uint32_t audio_terminal_ui_object_descendant_43ee54(void *, void *);

uint32_t audio_terminal_ui_object_valid_43e2ea(void *target) {
    for (uint8_t *display = (uint8_t *)audio_uart_lv_display_next_44fa22(0);
         display != 0;
         display = (uint8_t *)audio_uart_lv_display_next_44fa22(display)) {
        uint32_t count = *(uint32_t *)(void *)(display + 0x2d4u);
        uint32_t *roots = (uint32_t *)(uintptr_t)
            *(uint32_t *)(void *)(display + 0x2b8u);
        for (uint32_t i = 0u; i < count; ++i) {
            void *root = (void *)(uintptr_t)roots[i];
            if (root == target ||
                (uint8_t)audio_terminal_ui_object_descendant_43ee54(root, target) != 0u)
                return 1u;
        }
    }
    return 0u;
}
