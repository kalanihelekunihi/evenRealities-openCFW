/* Apollo Main LVGL linked-list insertion, stock 0x482b56..0x482bc8. */
#include <stdint.h>

extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_prepend_482b12(void *);
extern void *audio_uart_lv_malloc(uint32_t);

static uint32_t link(const uint8_t *list, const void *node, uint32_t offset)
{
    const uint32_t size = *(const uint32_t *)(const void *)list;
    return *(const uint32_t *)(const void *)((const uint8_t *)node + size + offset);
}

static void set_link(const uint8_t *list, void *node, uint32_t offset,
                     uint32_t value)
{
    if (node != 0) {
        const uint32_t size = *(const uint32_t *)(const void *)list;
        *(uint32_t *)(void *)((uint8_t *)node + size + offset) = value;
    }
}

void *audio_uart_lv_list_insert_before_482b56(void *list, void *before)
{
    if (list == 0 || before == 0) return 0;
    uint8_t *const bytes = (uint8_t *)list;
    if (audio_uart_lv_list_first(list) == before)
        return audio_uart_lv_list_prepend_482b12(list);
    const uint32_t size = *(const uint32_t *)(const void *)bytes;
    void *const node = audio_uart_lv_malloc(size + 8u);
    if (node == 0) return 0;
    const uint32_t previous = link(bytes, before, 0u);
    set_link(bytes, (void *)(uintptr_t)previous, 4u,
             (uint32_t)(uintptr_t)node);
    set_link(bytes, node, 0u, previous);
    set_link(bytes, before, 0u, (uint32_t)(uintptr_t)node);
    set_link(bytes, node, 4u, (uint32_t)(uintptr_t)before);
    return node;
}
