#ifndef R1_NATIVE_CLOCK_BOOTSTRAP_H
#define R1_NATIVE_CLOCK_BOOTSTRAP_H
#include "time_calendar/time_calendar.h"
typedef void (*r1_clock_tick_fn)(uint32_t);
typedef struct {
    time_calendar_backend_ops prefix;
    uintptr_t slot14,slot18;
    uint32_t (*bind_tick)(uint32_t,uint32_t,uint32_t,r1_clock_tick_fn);
} r1_native_clock_ops;
typedef struct {uint16_t offset,padding;uint32_t epoch;} r1_clock_boot_config;
extern const r1_native_clock_ops r1_clock_default_backend;
extern const r1_clock_boot_config r1_clock_boot_defaults;
uint32_t r1_clock_backend_snapshot(const r1_native_clock_ops **out,void **context);
uint32_t r1_clock_backend_bind(const r1_native_clock_ops *ops,void *context);
uint32_t r1_clock_initialize(const r1_clock_boot_config *config,void *incoming_r1);
void r1_clock_second_changed(uint32_t incoming_payload);
#endif
