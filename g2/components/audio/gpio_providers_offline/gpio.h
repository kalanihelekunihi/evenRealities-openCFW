#pragma once
#include <stdint.h>
/* Config: function[3:0], normal drive[11:10], pull[15:13]. All32 bits copied. */
uint32_t audio_gpio_pin_get(uint32_t pin,uint32_t *configuration);
uint32_t audio_gpio_pin_set(uint32_t pin,uint32_t configuration);
