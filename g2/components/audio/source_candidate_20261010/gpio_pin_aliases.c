/* Clock recovery pin calls target the validated Apollo GPIO entries.
 * Rebuild the existing source and export both caller names directly. */
#include "../gpio_providers_offline/gpio.c"

__asm__(".global stock_pin_get\n"
        ".set stock_pin_get, audio_gpio_pin_get\n"
        ".global stock_pin_set\n"
        ".set stock_pin_set, audio_gpio_pin_set\n"
        ".global codec_gpio_config\n.set codec_gpio_config, audio_gpio_pin_set\n");
