/* SPDX-License-Identifier: MIT */
/* Recovered from codec 2.2.6.10: query requires oscillator-reference gate. */
extern void open_cfw_gx8002_trim_clock_enable(void);
unsigned int open_cfw_gx8002_trim_state(void)
{
    open_cfw_gx8002_trim_clock_enable();
    return *(volatile unsigned int *)0xa0010030u & 1u;
}
