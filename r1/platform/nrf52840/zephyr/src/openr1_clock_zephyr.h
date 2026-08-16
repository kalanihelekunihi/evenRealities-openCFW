#ifndef OPENR1_CLOCK_ZEPHYR_H
#define OPENR1_CLOCK_ZEPHYR_H

#include <stdbool.h>
#include <stdint.h>
#include <time.h>

typedef struct r1_runtime r1_runtime;

int openr1_clock_zephyr_initialize(r1_runtime *runtime);
bool openr1_clock_zephyr_adopt_phone_time(uint32_t epoch_seconds,
                                          int16_t utc_offset_minutes);
bool openr1_clock_zephyr_epoch(uint32_t *epoch_seconds);
bool openr1_clock_zephyr_utc_offset(int16_t *utc_offset_minutes);
bool openr1_clock_zephyr_local_tm(struct tm *out);

#endif
