#include <stdint.h>
extern void *audio_uart_ambiq_default_unit_4c791a(void);
/* Native4b075e..4b077e: NULL chooses default, record clears without callbacks. */
void audio_uart_ambiq_blend_clear_4b075e(void *unit) {
    if(!unit)unit=audio_uart_ambiq_default_unit_4c791a();
    volatile uint8_t *u=unit;
    *(volatile uint32_t *)(u+80u)=0u;
    u[84]=255u;u[85]=255u;u[86]=255u;
}
