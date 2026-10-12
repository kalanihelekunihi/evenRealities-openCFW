/* Native stage2 0x10004830/34 loads two words from this conditional BSS
 * pair. Neither a retained value nor its producer is inferred here. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_gpio_irq_masks_200173a0[2]
    __attribute__((section(".bss.image_b_gpio_irq_masks"), used, aligned(4)));
