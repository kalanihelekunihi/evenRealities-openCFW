#ifndef OPENCFW_BOOT_ADC_CONFIGURATION_H
#define OPENCFW_BOOT_ADC_CONFIGURATION_H
#include <stdint.h>
typedef struct {uint8_t reserved0,mode,reserved2[2];uint32_t threshold;} opencfw_boot_adc_context_configuration;
typedef struct {uint8_t slot,reserved[3];uint32_t selector;uint8_t precision,averaging,shifted_enable,enable;} opencfw_boot_adc_channel_configuration;
uint32_t opencfw_bl_adc_context_configure(uint32_t context,const void *configuration);
uint32_t opencfw_bl_adc_configure_channel(uint32_t context,uint32_t channel,const void *configuration);
#endif
