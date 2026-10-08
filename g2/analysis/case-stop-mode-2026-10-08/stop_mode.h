#ifndef OPENCFW_CASE_STOP_MODE_H
#define OPENCFW_CASE_STOP_MODE_H
#include <stdint.h>
/* Raw locked-image ABI: regulator zero -> STOP0, nonzero -> STOP1;
 * entry exactly one -> WFI, other full-width values -> SEV/WFE/WFE.
 * This helper does not restore clocks, select wake pins, or prove real wake. */
void case_stop_mode(uint32_t regulator, uint32_t entry);
#endif
