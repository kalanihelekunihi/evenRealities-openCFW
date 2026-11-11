/* Nordic CMSIS intrinsics and recovered software-TWI delay callbacks.
 * See r1/docs/reference/twi-delay-review.md for arithmetic and timing limits. */
#include "nrf_gpio.h"

/* Stock 0x7081C returns directly. */
void r1_twi_delay_noop(uint32_t ignored) { (void)ignored; }

/* Stock 0x54AF0 is the distinct i2c_5 callback: five NOPs then return.
 * CMSIS intrinsics preserve the instruction slots, not calibrated bus timing. */
void r1_twi_i2c5_delay_noop(uint32_t ignored) {
    (void)ignored;
    __NOP();
    __NOP();
    __NOP();
    __NOP();
    __NOP();
}
