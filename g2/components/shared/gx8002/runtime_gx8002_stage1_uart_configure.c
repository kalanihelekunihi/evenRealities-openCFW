/* SPDX-License-Identifier: MIT */
/* Complete stage-one UART setup, package 0x39bb4..0x39c34.
 * Arithmetic helpers are explicit to preserve their boundary behavior,
 * including the still-unqualified zero-denominator case. */
extern unsigned int open_cfw_gx8002_stage1_frequency(unsigned int module);
extern unsigned int open_cfw_gx8002_stage1_39774(unsigned int, unsigned int);
extern unsigned int open_cfw_gx8002_stage1_397b8(unsigned int, unsigned int);
void open_cfw_gx8002_stage1_39bb4(unsigned int baud, unsigned int retain_divisor)
{
    volatile unsigned int *uart = (volatile unsigned int *)0xa0100000;
    uart[1] = 0;
    uart[4] = 3;
    if (retain_divisor == 0) {
        unsigned int denominator = baud << 4;
        unsigned int frequency = open_cfw_gx8002_stage1_frequency(17);
        unsigned int divisor = open_cfw_gx8002_stage1_39774(frequency, denominator);
        unsigned int remainder = open_cfw_gx8002_stage1_397b8(frequency, denominator);
        unsigned int fraction = open_cfw_gx8002_stage1_39774(remainder * 100u, denominator);
        fraction = open_cfw_gx8002_stage1_39774(fraction << 4, 100);
        while (uart[31] & 1u) { }
        uart[3] = 128;
        uart[0] = divisor & 255u;
        uart[1] = (divisor >> 8) & 255u;
        uart[48] = fraction & 255u;
    }
    while (uart[31] & 1u) { }
    uart[3] = 3;
    uart[2] = 79;
}
