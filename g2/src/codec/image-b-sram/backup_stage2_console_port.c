/* Native stage2 0x1000480c stores and 0x1000481e loads this RAM word.
 * It is conditional CRT BSS, so no warm-retention value is invented. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_console_port_2001739c
    __attribute__((section(".bss.image_b_console_port"), used, aligned(4)));
