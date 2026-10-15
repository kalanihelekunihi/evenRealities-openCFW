#ifndef R1_NAMED_ADC_H
#define R1_NAMED_ADC_H
#include "../registry/stock_registry.h"
#include "nrfx_saadc.h"
typedef struct {
    const char *name;
    uint8_t opened,input;
    nrf_saadc_channel_config_t config;
    uint8_t reserved_0f;
    generic_device_registry_device device;
} r1_named_adc_record;
typedef struct { uint8_t initialized,reserved[3];r1_named_adc_record records[3]; } r1_named_adc_state;
extern r1_named_adc_state r1_adc_state;
uint32_t r1_named_adc_register_all(void);
uint32_t r1_named_adc_open(generic_device_registry_device *device);
uint32_t r1_named_adc_close(generic_device_registry_device *device);
uint32_t r1_named_adc_sample(generic_device_registry_device *device,uintptr_t operation,uintptr_t output,uintptr_t extra);
#endif
