/* Five six-byte native output-table adapters. The ABI here is the recovered
 * record pointer -> pin word tail transfer, not the registrar's metadata type.
 * Provider implementations remain the pinned Nordic SDK HAL/GPIOTE sources. */
#include <stdint.h>
typedef struct {
    uint32_t name;
    uint8_t opened, padding[3];
    uint32_t pin;
} r1_output_gpio_prefix;
_Static_assert(__builtin_offsetof(r1_output_gpio_prefix, pin)==8,"native pin offset");
extern void r1_twi_gpio_high(uint32_t),r1_twi_gpio_low(uint32_t);
extern void nrfx_gpiote_out_set(uint32_t),nrfx_gpiote_out_clear(uint32_t),nrfx_gpiote_out_toggle(uint32_t);
void r1_output_gpio_driver10(const r1_output_gpio_prefix *record) { r1_twi_gpio_high(record->pin); }
void r1_output_gpio_driver0c(const r1_output_gpio_prefix *record) { r1_twi_gpio_low(record->pin); }
void r1_output_gpio_high(const r1_output_gpio_prefix *record) { nrfx_gpiote_out_set(record->pin); }
void r1_output_gpio_low(const r1_output_gpio_prefix *record) { nrfx_gpiote_out_clear(record->pin); }
void r1_output_gpio_toggle(const r1_output_gpio_prefix *record) { nrfx_gpiote_out_toggle(record->pin); }
