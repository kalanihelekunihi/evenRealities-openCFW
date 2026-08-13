#ifndef OPENR1_BAE8_H
#define OPENR1_BAE8_H

#include <stdint.h>

#include "openr1/r1_runtime.h"

uint32_t openr1_bae8_initialize(void);
uint32_t openr1_bae8_last_error(void);
r1_tx_status openr1_bae8_transmit(const r1_tx_event *event);

#endif
