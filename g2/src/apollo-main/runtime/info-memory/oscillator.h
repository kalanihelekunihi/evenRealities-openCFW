#pragma once
#include <stdint.h>
/* Controls0..6:32K enable/disable,32M kick/normal/disable,clock-out enable/disable. */
uint32_t audio_oscillator_control(uint32_t action,const void *arguments);
