/* Source wrappers over authenticated Nordic nRF5 SDK 17.1.0 inline HAL.
 * Native TWI callback references are recorded in stock-initialization.json.
 * Consume upstream HAL bodies directly so corrections can be adopted by pin. */
#include "nrf_gpio.h"
void r1_twi_gpio_low(uint32_t pin) { nrf_gpio_pin_clear(pin); }
void r1_twi_gpio_high(uint32_t pin) { nrf_gpio_pin_set(pin); }
void r1_twi_gpio_output(uint32_t pin) { nrf_gpio_cfg_output(pin); }
void r1_twi_gpio_input(uint32_t pin, uint32_t pull) { nrf_gpio_cfg_input(pin,(nrf_gpio_pin_pull_t)pull); }
void r1_twi_gpio_release(uint32_t pin) { nrf_gpio_cfg_default(pin); }
uint32_t r1_twi_gpio_read(uint32_t pin) { return nrf_gpio_pin_read(pin); }

/* Recovered 0x7A6DC/EC wrappers and 0x9A640/50 subtract-three kernels.
 * Volatile keeps the recovered iterations observable to the compiler. This
 * establishes the arithmetic/work contract, not original cycle timing. */
void r1_twi_delay_busy(uint32_t microseconds) {
    if (microseconds != 0) {
        volatile uint32_t remaining=microseconds<<6;
        uint32_t before;
        do {
            before=remaining;
            remaining=before-3;
        } while (before>3);
    }
}
/* Stock 0x7081C and 0x54AF0 have no observable side effect. */
void r1_twi_delay_noop(uint32_t ignored) { (void)ignored; }
