/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Synthetic link providers only. They establish call order/arguments and
 * configured return propagation, never real queue drain or delay completion. */
struct lifecycle_fixture { uint32_t disable_status, count, events[3][3]; };
struct lifecycle_fixture ambiq_lifecycle_fixture;
static void record(uint32_t kind,uint32_t argument,uint32_t prefix) {
    uint32_t i=ambiq_lifecycle_fixture.count++;
    if(i<3) { ambiq_lifecycle_fixture.events[i][0]=kind;
        ambiq_lifecycle_fixture.events[i][1]=argument;
        ambiq_lifecycle_fixture.events[i][2]=prefix; }
}
#ifndef OPENCFW_REAL_CMDQ
uint32_t mspi_cq_disable(void *h) {
    record(1,(uint32_t)(uintptr_t)h,*(uint32_t *)h);
    return ambiq_lifecycle_fixture.disable_status;
}
uint32_t mspi_cq_term(void *h) {
    record(2,(uint32_t)(uintptr_t)h,*(uint32_t *)h);return 0;
}
#endif
#if defined(OPENCFW_REAL_CMDQ) && !defined(OPENCFW_REAL_CRITICAL)
/* Synthetic prior mask: no concurrency/hardware critical-section proof. */
uint32_t opencfw_cmdq_critical_enter(void) { return 0; }
#endif
void am_hal_delay_us(uint32_t duration) {record(3,duration,0);}
