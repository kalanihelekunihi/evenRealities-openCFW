/* Authenticated native R1 ADC descriptors and adapters. Nordic owns SAADC.
 * Stock close passes the stored input selector, unlike open's record index;
 * preserve that evidence rather than silently correcting inferred intent. */
#include <stddef.h>
#include "stock_named_adc.h"
extern int strcmp(const char *,const char *);
extern void r1_adc_error(uint32_t status);
extern void r1_twi_delay_busy(uint32_t microseconds);
typedef struct {
    uintptr_t reserved_00,reserved_04;
    uint32_t (*open)(generic_device_registry_device *);
    uint32_t (*close)(generic_device_registry_device *);
    generic_device_registry_operation sample;
    uintptr_t reserved_14,reserved_18,reserved_1c,reserved_20;
} adc_ops;
static const adc_ops operations __attribute__((section(".r1.adc.ops"),aligned(4)))={
    .open=r1_named_adc_open,.close=r1_named_adc_close,.sample=r1_named_adc_sample
};
_Static_assert(sizeof(nrf_saadc_channel_config_t)==9,"stock channel configuration");
_Static_assert(sizeof(r1_named_adc_record)==40,"stock ADC record stride");
_Static_assert(offsetof(r1_named_adc_record,config)==6,"channel configuration offset");
_Static_assert(offsetof(r1_named_adc_record,device)==16,"embedded registry");
#define RECORD(text,input_pin,gain_value,time_value) {.name=text,.input=input_pin, \
    .config={.gain=gain_value,.acq_time=time_value}}
r1_named_adc_state r1_adc_state __attribute__((section(".r1.adc.state"),aligned(4)))={
    .records={RECORD("vbat_adc",6,NRF_SAADC_GAIN1_2,NRF_SAADC_ACQTIME_40US),
    RECORD("vpmic_isns_adc",4,NRF_SAADC_GAIN1_2,NRF_SAADC_ACQTIME_40US),
    RECORD("vnfc_rect_adc",3,NRF_SAADC_GAIN1_6,NRF_SAADC_ACQTIME_10US)}
};
static int find_record(generic_device_registry_device *device) {
    for (int i=0;i<3;++i) if (strcmp(r1_adc_state.records[i].name,device->name)==0) return i;
    return -1;
}
uint32_t r1_named_adc_register_all(void) {
    r1_adc_state.initialized=0;
    uint32_t status=0;
    for (unsigned i=0;i<3;++i) {
        r1_adc_state.records[i].device.name=r1_adc_state.records[i].name;
        r1_adc_state.records[i].device.ops=(const generic_device_registry_ops *)&operations;
        status=r1_stock_registry_register(&r1_adc_state.records[i].device);
    }
    return status;
}
uint32_t r1_named_adc_open(generic_device_registry_device *device) {
    int index=find_record(device);if (index<0) return 1;
    r1_named_adc_record *record=&r1_adc_state.records[index];if (record->opened) return 0;
    if (!r1_adc_state.initialized) {
        const nrfx_saadc_config_t config={.resolution=NRF_SAADC_RESOLUTION_12BIT,.oversample=NRF_SAADC_OVERSAMPLE_DISABLED,.interrupt_priority=6,.low_power_mode=false};
        uint32_t status=nrfx_saadc_init(&config,NULL);if (status) r1_adc_error(status);
        r1_adc_state.initialized=1;
    }
    record->config.pin_p=(nrf_saadc_input_t)record->input;
    uint32_t status=nrfx_saadc_channel_init((uint8_t)index,&record->config);
    record->opened=1;
    if (status) r1_adc_error(status);
    r1_twi_delay_busy(1000);r1_twi_delay_busy(1000);
    return 0;
}
uint32_t r1_named_adc_close(generic_device_registry_device *device) {
    int index=find_record(device);if (index<0) return 1;
    r1_named_adc_record *record=&r1_adc_state.records[index];
    if (record->opened) {
        nrfx_saadc_channel_uninit(record->input);
        record->opened=0;
        unsigned all_closed=1;
        for (unsigned i=0;i<3;++i) if (r1_adc_state.records[i].opened) { all_closed=0;break; }
        if (all_closed & r1_adc_state.initialized) { nrfx_saadc_uninit();r1_adc_state.initialized=0; }
    }
    return 0;
}
uint32_t r1_named_adc_sample(generic_device_registry_device *device,uintptr_t operation,uintptr_t output,uintptr_t extra) {
    (void)operation;(void)extra;int index=find_record(device);
    if (index<0 || !r1_adc_state.records[index].opened) return 8;
    nrf_saadc_value_t sample;
    (void)nrfx_saadc_sample_convert((uint8_t)index,&sample);
    *(uint16_t *)output=(uint16_t)sample;
    return 0;
}
