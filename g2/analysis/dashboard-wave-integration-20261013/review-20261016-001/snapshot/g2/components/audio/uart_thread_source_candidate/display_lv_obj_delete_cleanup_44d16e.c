/* Apollo Main object class cleanup, native 0x44d16e..0x44d199. */
#include <stdint.h>

void audio_uart_lv_obj_delete_cleanup_44d16e(void *object) {
    uint8_t *item = (uint8_t *)object;
    uint8_t *node = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)item;
    uint32_t callback = *(uint32_t *)(void *)(node + 8u);
    if (callback != 0u) {
        ((void (*)(void *, void *))(uintptr_t)callback)(node, object);
    }
    uint32_t next = *(uint32_t *)(void *)node;
    if (next != 0u) {
        *(uint32_t *)(void *)item = next;
        audio_uart_lv_obj_delete_cleanup_44d16e(object);
    }
}
