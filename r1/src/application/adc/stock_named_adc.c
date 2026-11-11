/* Authenticated native R1 ADC descriptors and adapters. Nordic owns SAADC.
 * Stock close passes the stored input selector, unlike open's record index;
 * preserve that evidence rather than silently correcting inferred intent. */
#include <stddef.h>
#include "stock_named_adc.h"
extern int strcmp(const char *,const char *);
extern void r1_adc_error(uint32_t status);
extern void r1_rtt_delay_cycles(uint32_t cycles);
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
/* Native open/close reload device name before record name for each compare. */
static int find_record(generic_device_registry_device *device) {
    for (int i=0;i<3;++i) {
        const char *device_name=((volatile generic_device_registry_device *)device)->name;
        volatile r1_named_adc_record *record=&r1_adc_state.records[i];
        const char *record_name=record->name;
        if (strcmp(record_name,device_name)==0) return i;
    }
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
union r1_adc_open_config { nrfx_saadc_config_t config;uint32_t word; };
_Static_assert(sizeof(nrfx_saadc_config_t)==4 &&
    offsetof(nrfx_saadc_config_t,interrupt_priority)==2 &&
    offsetof(nrfx_saadc_config_t,low_power_mode)==3 &&
    NRF_SAADC_RESOLUTION_10BIT==1 && NRF_SAADC_RESOLUTION_12BIT==2,
    "native ADC initialization word");
const union r1_adc_open_config r1_adc_open_template
 __attribute__((section(".r1.adc.open.config"),aligned(4)))={.config={
    .resolution=NRF_SAADC_RESOLUTION_10BIT,
    .oversample=NRF_SAADC_OVERSAMPLE_DISABLED,
    .interrupt_priority=6,.low_power_mode=false}};
/* Stock 0x54864 replaces the template resolution byte with 12-bit mode.
 * The configuration pointer is private synchronous call storage. */
__attribute__((used,noinline)) uint32_t r1_named_adc_open_body(
 generic_device_registry_device *device,volatile uint32_t *frame)
{
    int index=find_record(device);if (index<0) return 1;
    volatile r1_named_adc_state *state=&r1_adc_state;
    volatile r1_named_adc_record *record=&state->records[index];
    if (record->opened) return 0;
    if (!state->initialized) {
        *frame=r1_adc_open_template.word;
        ((volatile uint8_t *)frame)[0]=NRF_SAADC_RESOLUTION_12BIT;
        uint32_t status=nrfx_saadc_init((const nrfx_saadc_config_t *)(uintptr_t)frame,NULL);
        if (status) r1_adc_error(status);
        state->initialized=1;
    }
    record->config.pin_p=(nrf_saadc_input_t)record->input;
    uint32_t status=nrfx_saadc_channel_init((uint8_t)index,
                         (const nrf_saadc_channel_config_t *)(uintptr_t)&record->config);
    record->opened=1;
    if (status) r1_adc_error(status);
    r1_rtt_delay_cycles(64000);r1_rtt_delay_cycles(64000);
    return 0;
}
uint32_t r1_named_adc_open(generic_device_registry_device *device)
{
    uint32_t configuration;
    return r1_named_adc_open_body(device,&configuration);
}
uint32_t r1_named_adc_close(generic_device_registry_device *device) {
    int index=find_record(device);if (index<0) return 1;
    volatile r1_named_adc_state *state=&r1_adc_state;
    volatile r1_named_adc_record *record=&state->records[index];
    if (record->opened) {
        nrfx_saadc_channel_uninit(record->input);
        record->opened=0;
        unsigned all_closed=1;
        for (unsigned i=0;i<3;++i) if (state->records[i].opened) { all_closed=0;break; }
        if (all_closed & state->initialized) { nrfx_saadc_uninit();state->initialized=0; }
    }
    return 0;
}
/* Stock 0x548f0 uses the low half of argument four even when conversion
 * returns an error without writing. Keep the lookup's volatile read order. */
__attribute__((used,noinline)) uint32_t r1_named_adc_sample_body(
 generic_device_registry_device *device, uintptr_t operation, uintptr_t output,
 const volatile uint16_t *sample)
{
    (void)operation;
    for (uint32_t index=0;index<3;++index) {
        const char *device_name=((volatile generic_device_registry_device *)device)->name;
        volatile r1_named_adc_record *record=&r1_adc_state.records[index];
        const char *record_name=record->name;
        if (strcmp(record_name,device_name)!=0) continue;
        if (!record->opened) return 8;
        (void)nrfx_saadc_sample_convert((uint8_t)index,
                         (nrf_saadc_value_t *)(uintptr_t)sample);
        *(volatile uint16_t *)output=*sample;
        return 0;
    }
    return 8;
}
uint32_t r1_named_adc_sample(generic_device_registry_device *device,
 uintptr_t operation, uintptr_t output, uintptr_t extra)
{
    /* The fourth operation argument supplies the stock fallback sample when
     * conversion fails without writing. Initialize it explicitly in C. */
    uint32_t sample=(uint32_t)extra;
    return r1_named_adc_sample_body(device,operation,output,
                                  (const volatile uint16_t *)&sample);
}
