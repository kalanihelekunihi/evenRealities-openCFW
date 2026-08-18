#include "openr1_rtc_service.h"

#define OPENR1_RTC_NAME "sys rtc"

static void bytes_zero(void *destination, size_t length) {
    uint8_t *bytes = (uint8_t *)destination;
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

static void bytes_copy(void *destination, const void *source, size_t length) {
    uint8_t *out = (uint8_t *)destination;
    const uint8_t *in = (const uint8_t *)source;
    for (size_t index = 0u; index < length; ++index) {
        out[index] = in[index];
    }
}

static openr1_rtc_service *service_from_record(
    generic_device_registry_device *record) {
    if (record == NULL) {
        return NULL;
    }
    return (openr1_rtc_service *)record->priv[0];
}

static uint32_t registry_set_time_operation(
    generic_device_registry_device *record,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    (void)arg1;
    (void)arg3;
    openr1_rtc_service *service = service_from_record(record);
    const generic_device_registry_time_block *request =
        (const generic_device_registry_time_block *)arg2;
    if (service == NULL || request == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    rtc_device_time_block block;
    bytes_zero(&block, sizeof(block));
    block.epoch_seconds = request->epoch_seconds;
    block.utc_offset_minutes = (int16_t)request->utc_offset_minutes;
    const char *name = OPENR1_RTC_NAME;
    return rtc_device_epoch_initialize(&service->rtc, &name, &block);
}

static uint32_t registry_snapshot_operation(
    generic_device_registry_device *record,
    uintptr_t arg1, uintptr_t arg2, uintptr_t arg3) {
    (void)arg1;
    (void)arg3;
    openr1_rtc_service *service = service_from_record(record);
    if (service == NULL) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    return rtc_device_snapshot(
        &service->rtc, (rtc_device_time_block *)arg2);
}

static uint32_t registry_control_adapter(
    void *device, uint32_t operation, void *argument) {
    return generic_device_registry_dispatch_slot_20(
        (generic_device_registry_device *)device,
        (uintptr_t)operation, (uintptr_t)argument, 0u);
}

static uint32_t registry_set_time_adapter(
    void *device, uint32_t epoch_seconds, int16_t utc_offset_minutes) {
    generic_device_registry_time_block block;
    bytes_zero(&block, sizeof(block));
    block.epoch_seconds = epoch_seconds;
    block.utc_offset_minutes = (uint16_t)utc_offset_minutes;
    return generic_device_registry_dispatch_slot_14(
        (generic_device_registry_device *)device,
        0u, (uintptr_t)&block, 0u);
}

uint32_t openr1_rtc_service_initialize(
    openr1_rtc_service *service,
    const rtc_device_providers *providers,
    const void *rtc_instance,
    size_t rtc_instance_bytes) {
    if (service == NULL || providers == NULL || rtc_instance == NULL ||
            rtc_instance_bytes != sizeof(service->rtc.state.records[0].rtc_instance)) {
        return RTC_DEVICE_STATUS_BAD_ARGUMENT;
    }
    bytes_zero(service, sizeof(*service));
    rtc_device_initialize(&service->rtc, providers);
    bytes_copy(service->rtc.state.records[0].rtc_instance,
               rtc_instance, rtc_instance_bytes);

    generic_device_registry_initialize(&service->registry, NULL);
    service->registry_ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_14] =
        registry_set_time_operation;
    service->registry_ops.slot[GENERIC_DEVICE_REGISTRY_SLOT_20] =
        registry_snapshot_operation;
    service->registry_record.name = OPENR1_RTC_NAME;
    service->registry_record.ops = &service->registry_ops;
    service->registry_record.priv[0] = (uintptr_t)service;
    if (generic_device_registry_register(
            &service->registry, &service->registry_record) != 1u) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    generic_device_registry_wiring wiring;
    bytes_zero(&wiring, sizeof(wiring));
    wiring.time_device = &service->registry_record;
    generic_device_registry_bind_wiring(&service->registry, &wiring);
    rtc_device_bind_registry(
        &service->rtc, &service->registry_record,
        registry_control_adapter, registry_set_time_adapter);

    const char *name = OPENR1_RTC_NAME;
    const uint32_t status = rtc_device_open(&service->rtc, &name);
    if (status != RTC_DEVICE_STATUS_OK) {
        return status;
    }
    service->initialized = true;
    return RTC_DEVICE_STATUS_OK;
}

uint32_t openr1_rtc_service_set_time(
    openr1_rtc_service *service,
    uint32_t epoch_seconds,
    int16_t utc_offset_minutes) {
    if (service == NULL || !service->initialized) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    generic_device_registry_time_block block;
    bytes_zero(&block, sizeof(block));
    block.epoch_seconds = epoch_seconds;
    block.utc_offset_minutes = (uint16_t)utc_offset_minutes;
    return generic_device_registry_dispatch_slot_14(
        service->registry.wiring.time_device,
        0u, (uintptr_t)&block, 0u);
}

uint32_t openr1_rtc_service_snapshot(
    openr1_rtc_service *service,
    rtc_device_time_block *out) {
    if (service == NULL || !service->initialized) {
        return RTC_DEVICE_STATUS_LOOKUP_FAILED;
    }
    return generic_device_registry_dispatch_slot_20(
        &service->registry_record, 0u, (uintptr_t)out, 0u);
}

void openr1_rtc_service_tick(openr1_rtc_service *service) {
    if (service != NULL && service->initialized) {
        rtc_device_tick(&service->rtc);
    }
}
