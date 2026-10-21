/* Native ring used-byte computation 0x57e38c..0x57e3a3. */
#include <stdint.h>
uint32_t audio_uart_ring_available(const void *descriptor)
{
    const uint8_t *d=(const uint8_t *)descriptor;
    uint32_t capacity=*(const uint32_t *)(d+8u);
    uint32_t result=*(const uint32_t *)(d+4u)+capacity-*(const uint32_t *)d;
    return result>=capacity ? result-capacity : result;
}
/* Native writable-byte computation 0x57e028..0x57e05d. */
extern void offline_assert(void) __attribute__((noreturn));
uint32_t audio_uart_ring_space(const void *descriptor)
{
    if (!descriptor) offline_assert();
    const volatile uint32_t *d=(const volatile uint32_t *)descriptor;
    uint32_t head,capacity,result;
    do {
        head=d[0];
        capacity=d[2];
        result=d[0]+capacity-d[1];
    } while (head!=d[0]);
    result--;
    return result>=capacity ? result-capacity : result;
}
