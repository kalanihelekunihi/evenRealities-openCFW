/* Native request_irq bounds lines to 0..31 and stores two words per line.
 * Generic IRQ dispatch indexes the same table; controller line validity is
 * a separate runtime contract. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_irq_descriptors_200173a8[64]
    __attribute__((section(".bss.image_b_irq_descriptors"), used, aligned(4)));
