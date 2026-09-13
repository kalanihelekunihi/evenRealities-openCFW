/* SPDX-License-Identifier: MIT */
/* Recovered oscillator-reference gate wrapper from codec 2.2.6.10. */
extern int gx_clock_set_module_enable(unsigned int module, unsigned int enable);
void open_cfw_gx8002_trim_clock_enable(void)
{
    (void)gx_clock_set_module_enable(9u, 1u);
}
