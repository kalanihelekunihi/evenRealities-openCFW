#ifndef OPENR1_MOTION_ZEPHYR_H
#define OPENR1_MOTION_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_motion.h"

int openr1_motion_zephyr_initialize(void);
int openr1_motion_zephyr_read_fifo(r1_motion_sample *samples,
                                   size_t capacity,
                                   size_t *sample_count);
int openr1_motion_zephyr_disable_double_tap(void);
r1_motion_variant openr1_motion_zephyr_variant(void);
bool openr1_motion_zephyr_is_enabled(void);
uint32_t openr1_motion_zephyr_interrupt_count(void);

#endif
