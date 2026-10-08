#ifndef OPENCFW_CASE_WAKE_RECONSTRUCTION_H
#define OPENCFW_CASE_WAKE_RECONSTRUCTION_H
#include <stdint.h>
/* Raw reconstructed register contracts. Low six bits select pins; enable
 * argument bits shifted right by eight provide polarity. A production caller
 * must use valid board-specific wake pin constants and serialize PWR access.
 * Standalone offline module: not integrated into the firmware build. */
void case_wake_enable(uint32_t pin_and_polarity);
void case_wake_disable(uint32_t pin_mask);
#endif
