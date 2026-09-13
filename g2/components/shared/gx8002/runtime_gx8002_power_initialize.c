/* SPDX-License-Identifier: MIT */
/* Recovered LvpPmuInit; upstream lineage: lvp_pmu.c at
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. */
#include "runtime_gx8002_power_registration.h"
extern unsigned gx_pmu_get_wakeup_source(void);
extern void *memset(void *, int, size_t);
int open_cfw_gx8002_power_initialize(void)
{
    if (gx_pmu_get_wakeup_source() < 2) {
        memset(&open_cfw_gx8002_power_state, 0, sizeof(open_cfw_gx8002_power_state));
        return 1;
    }
    for (unsigned i = 0; i < open_cfw_gx8002_power_state.resume_count; ++i) {
        struct open_cfw_app_power_registration *entry = &open_cfw_gx8002_power_state.resume[i];
        entry->callback(entry->private_data);
    }
    return 0;
}
