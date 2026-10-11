/* Native TinyFrame timer removal 0x49183e. The callback's stack record has
 * only three fields written by stock; other bytes are deliberately opaque. */
#include <stdint.h>

void audio_uart_module_timer_expire(void *module, uint32_t slot, void *timer_) {
    uint8_t *timer = (uint8_t *)timer_;
    void (*cancel)(void *, void *) = *(void (**)(void *, void *))(timer + 4u);
    if (cancel == 0) return;
    if (*(uint32_t *)(timer + 16u) != 0u ||
        *(uint32_t *)(timer + 20u) != 0u) {
        uint8_t record[24];
        *(uint32_t *)(record + 8u) = 0u;
        *(uint32_t *)(record + 16u) = *(uint32_t *)(timer + 16u);
        *(uint32_t *)(record + 20u) = *(uint32_t *)(timer + 20u);
        cancel(module, record);
    }
    *(uint32_t *)(timer + 4u) = 0u;
    *(uint32_t *)(timer + 8u) = 0u;
    uint8_t *count = (uint8_t *)module + 0x7158u;
    if ((slot & 0xffu) == (uint32_t)(uint8_t)(*count - 1u)) --*count;
}
