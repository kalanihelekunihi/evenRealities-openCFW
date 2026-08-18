#ifndef OPENR1_RTC_SERVICE_H
#define OPENR1_RTC_SERVICE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "generic_device_registry/generic_device_registry.h"
#include "rtc_device/rtc_device.h"

/* Source-built composition of the recovered `sys rtc` record and recovered
 * generic device registry. Hardware access remains in the target adapters. */
typedef struct {
    rtc_device rtc;
    generic_device_registry registry;
    generic_device_registry_ops registry_ops;
    generic_device_registry_device registry_record;
    bool initialized;
} openr1_rtc_service;

/* Initializes the recovered RTC object, copies the target's source-defined
 * RTC instance descriptor into the recovered eight-byte field, registers the
 * `sys rtc` record, binds the registry veneers, and starts the 8 Hz source. */
uint32_t openr1_rtc_service_initialize(
    openr1_rtc_service *service,
    const rtc_device_providers *providers,
    const void *rtc_instance,
    size_t rtc_instance_bytes);

/* Routes a phone-supplied epoch/offset through the reconstructed registry
 * slot-0x14 request path into rtc_device_epoch_initialize. */
uint32_t openr1_rtc_service_set_time(
    openr1_rtc_service *service,
    uint32_t epoch_seconds,
    int16_t utc_offset_minutes);

/* Reads the recovered epoch/subsecond representation. */
uint32_t openr1_rtc_service_snapshot(
    openr1_rtc_service *service,
    rtc_device_time_block *out);

/* Called by the target RTC2 interrupt/counter callback at exactly 8 Hz. */
void openr1_rtc_service_tick(openr1_rtc_service *service);

#endif
