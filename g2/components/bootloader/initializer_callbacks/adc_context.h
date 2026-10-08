/* Locked bootloader ADC static-context claim and calibration interfaces. */
#ifndef OPENCFW_BOOT_ADC_CONTEXT_H
#define OPENCFW_BOOT_ADC_CONTEXT_H
#include <stdint.h>
typedef struct {uint32_t flags,module;uint8_t retained[64];} opencfw_boot_adc_context;
_Static_assert(sizeof(opencfw_boot_adc_context)==72,"locked ADC context stride");
extern volatile opencfw_boot_adc_context opencfw_boot_adc_context_pool;
uint32_t opencfw_bl_adc_context_initialize(uint32_t module,uint32_t *context_out);
uint32_t opencfw_bl_adc_reset(uint32_t context);
#endif
