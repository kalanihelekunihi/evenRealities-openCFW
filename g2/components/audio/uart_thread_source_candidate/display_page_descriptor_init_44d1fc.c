/* Apollo page class initialization walk 0x44d1fc..0x44d22f. */
#include <stdint.h>

typedef void (*audio_page_class_init)(const void *, void *);

void audio_uart_page_descriptor_init_44d1fc(const void *root, void *page) {
    const uint8_t *const descriptor = *(const uint8_t *const *)page;
    const uint8_t *const parent = *(const uint8_t *const *)(const void *)descriptor;
    if (parent != 0) {
        *(const uint8_t **)(void *)page = parent;
        audio_uart_page_descriptor_init_44d1fc(root, page);
        *(const uint8_t **)(void *)page = descriptor;
    }
    const audio_page_class_init callback =
        *(const audio_page_class_init *)(const void *)(descriptor + 4u);
    if (callback != 0)
        callback(root, page);
}
