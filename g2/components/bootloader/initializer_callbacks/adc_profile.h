#ifndef OPENCFW_BOOT_ADC_PROFILE_H
#define OPENCFW_BOOT_ADC_PROFILE_H
#include <stdint.h>
typedef struct {uint8_t clock,repeat_trigger,polarity,trigger,clock_mode,power_mode,repeat;} opencfw_boot_adc_profile;
uint32_t opencfw_bl_adc_profile_transfer(uint32_t context,uint32_t operation,uint32_t save_restore);
uint32_t opencfw_bl_adc_apply_profile(uint32_t context,const void *profile);
#endif
