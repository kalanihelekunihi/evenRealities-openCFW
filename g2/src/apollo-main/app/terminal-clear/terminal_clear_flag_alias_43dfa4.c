/* Terminal's historical symbol for stock lv_obj_remove_flag at 0x43dfa4. */
#include <stdint.h>
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);
void audio_lv_obj_invalidate_43dfa4(uint32_t object, uint32_t flags) {
    audio_uart_page_43dfa4((void *)(uintptr_t)object, flags);
}
