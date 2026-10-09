#pragma once
#include <stdint.h>
typedef struct {uint8_t rom_mode,dtcm_active,dtcm_retain,nvm_active,keep_nvm_on_sleep;} audio_mcu_memory_cfg;
typedef struct {uint8_t active,with_mcu,with_gpu,with_display,retain;} audio_sram_cfg;
/* ROM0=always-on/1=auto; DTCM retain0=retain/1=powerdown; NVM0/1/3. */
uint32_t audio_mcu_memory_config(const audio_mcu_memory_cfg *cfg);
uint32_t audio_sram_config(const audio_sram_cfg *cfg);
