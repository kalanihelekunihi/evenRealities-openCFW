#ifndef OPENCFW_CASE_VOLTAGE_SCALING_H
#define OPENCFW_CASE_VOLTAGE_SCALING_H
#include <stdint.h>
/* Raw register ABI; validation of scale and clock is the caller's job.
 * Returns 0 for completion / no required poll, 3 for exhausted busy retry.
 * Call before the application clock setup, preserving wake configuration. */
uint32_t case_voltage_scaling(uint32_t scale);
#endif
