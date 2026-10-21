/* Native 0x100040e8 saves 10 registers (40 bytes), allocates 52 bytes,
 * and leaves descriptor[8] at SP+36 unwritten for out-of-domain ports.
 * That word is entry-SP-56. Read that exact ambient stack location before
 * C creates its own frame, then pass it as the fourth ABI argument. The
 * word's contents remain unowned runtime state, not a fabricated default.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_dma_apply_body_100040e8(
    volatile uint32_t *, uint32_t, uint32_t, uint32_t);

__attribute__((naked))
int32_t gx8002_image_b_uart_dma_apply_100040e8(
    volatile uint32_t *record, uint32_t source, uint32_t length)
{
    (void)record;
    (void)source;
    (void)length;
    __asm__ volatile (
        "subi r14, r14, 56\n\t"
        "ld.w r3, (r14, 0)\n\t"
        "addi r14, r14, 56\n\t"
        "br gx8002_image_b_uart_dma_apply_body_100040e8");
}
