#pragma once
#include <stdint.h>
typedef struct {
 uint32_t valid,sbl_version[2],main_pointer,sbl_ota,soc_id[8],patch_tracker;
 uint32_t temperature_cal[3],factory_date,adc_cal[2],audio_adc_cal[12];
} audio_info1_cache;
uint32_t audio_info1_populate(void);
