#pragma once
#include <stdint.h>
/* Explicit incoming R5 models stock scratch upper bits for GPIO15 configuration. */
void clock_reset_recover(uint32_t incoming_r5);
