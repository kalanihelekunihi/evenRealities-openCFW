/* Locked42ec0c request interfaces; raw flags are not float1.0 values. */
#ifndef OPENCFW_BOOT_ADC_CONTROL_H
#define OPENCFW_BOOT_ADC_CONTROL_H
#include <stdint.h>
#define OPENCFW_ADC_SENTINEL_BITS UINT32_C(0xc2f6e979)
typedef struct {uint8_t enabled,reserved[3];uint32_t upper,lower;} opencfw_boot_adc_window;
typedef struct {float sensor_input,temperature_celsius;uint32_t sentinel_bits;} opencfw_boot_adc_temperature;
typedef struct {uint32_t trim_bits[3],sentinel_or_measured;} opencfw_boot_adc_temperature_trims;
typedef struct {uint32_t offset_bits,gain_bits,zero2,sentinel_or_zero;} opencfw_boot_adc_correction;
uint32_t opencfw_bl_adc_configure(uint32_t context,uint32_t request,void *arguments);
#endif
