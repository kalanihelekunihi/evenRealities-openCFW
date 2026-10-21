#ifndef OPENCFW_BOOT_ADC_SAMPLES_H
#define OPENCFW_BOOT_ADC_SAMPLES_H
#include <stdint.h>
typedef struct {uint32_t sample,slot;} opencfw_boot_adc_sample;
uint32_t opencfw_boot_adc_correct_sample(uint32_t fifo_word,uint32_t enabled);
uint32_t opencfw_bl_adc_enumerate(uint32_t context,uint32_t full_sample,const uint32_t *buffer,uint32_t *count,opencfw_boot_adc_sample *output);
uint32_t opencfw_bl_adc_activate(uint32_t context);
uint32_t opencfw_bl_adc_enable(uint32_t context);
uint32_t opencfw_bl_adc_disable(uint32_t context);
uint32_t opencfw_bl_adc_command(uint32_t context);
/* Legacy symbol name: this function DEACTIVATES and releases clock, not numerical normalization. */
uint32_t opencfw_bl_adc_normalize(uint32_t context);
#endif
