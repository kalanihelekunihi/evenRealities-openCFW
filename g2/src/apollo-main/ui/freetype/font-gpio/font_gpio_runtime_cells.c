#include <stdint.h>

void *audio_uart_font_flash_device
    __attribute__((section(".g2_ram_20074544"), used));
void *audio_uart_font_flash_mutex
    __attribute__((section(".g2_ram_20074548"), used));

const volatile uint32_t *const audio_uart_gpio_input_base =
    (const volatile uint32_t *)(uintptr_t)0x40010404u;
const volatile uint32_t *const audio_uart_gpio_output_base =
    (const volatile uint32_t *)(uintptr_t)0x40010420u;
const volatile uint32_t *const audio_uart_gpio_enable_base =
    (const volatile uint32_t *)(uintptr_t)0x40010474u;
