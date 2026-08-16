#ifndef OPENR1_OPTICAL_ZEPHYR_H
#define OPENR1_OPTICAL_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_goodix.h"

int openr1_optical_zephyr_initialize(void);
int openr1_optical_zephyr_start(r1_goodix_stock_profile profile);
int openr1_optical_zephyr_switch(r1_goodix_switch_selection profile);
int openr1_optical_zephyr_stop(void);
bool openr1_optical_zephyr_provider_available(void);
bool openr1_optical_zephyr_prepared(void);
uint32_t openr1_optical_zephyr_interrupt_count(void);
uint32_t openr1_optical_zephyr_raw_frame_count(void);
int openr1_optical_zephyr_last_error(void);

#endif
