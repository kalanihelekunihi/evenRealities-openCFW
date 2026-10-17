/* The ROM entry consumes the caller's R5 as GPIO15 scratch configuration.
 * Keep that register value when entering the C reconstruction, whose explicit
 * argument makes the otherwise hidden dependency testable.
 */
void stock_clock_mux_reset(void) __attribute__((naked));
void stock_clock_mux_reset(void)
{
    __asm volatile("mov r0, r5\n\tb clock_reset_recover");
}
