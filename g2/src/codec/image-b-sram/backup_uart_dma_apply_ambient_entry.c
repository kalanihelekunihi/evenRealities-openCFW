/* Native 0x100040e8 entry: for out-of-domain port selectors the native
 * descriptor direction word is unwritten stack. That word is 0 here; ports
 * 0 and 1 use the native values 7 and 5 in the body. */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_dma_apply_body_100040e8(
    volatile uint32_t *, uint32_t, uint32_t, uint32_t);

int32_t gx8002_image_b_uart_dma_apply_100040e8(
    volatile uint32_t *record, uint32_t source, uint32_t length)
{
    return gx8002_image_b_uart_dma_apply_body_100040e8(record, source,
                                                       length, 0u);
}
