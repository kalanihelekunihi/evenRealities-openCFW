/* SPDX-License-Identifier: MIT */
/* Recovery preserves the stock search-before-validation order, including
 * a null callback matching an empty slot without increasing the count. */
#include "runtime_gx8002_power_registration.h"
extern void *open_cfw_gx8002_memcpy(void *, const void *, size_t);
#define REGISTER(NAME, ARRAY, COUNT) \
int NAME(struct open_cfw_app_power_registration *record) \
{ \
    for (unsigned i=0; i<8; ++i) { \
        if (open_cfw_gx8002_power_state.ARRAY[i].callback==record->callback) { \
            open_cfw_gx8002_memcpy(&open_cfw_gx8002_power_state.ARRAY[i],record,sizeof(*record)); \
            return 0; \
        } \
    } \
    if (open_cfw_gx8002_power_state.COUNT>=8 || !record->callback) return -1; \
    open_cfw_gx8002_memcpy(&open_cfw_gx8002_power_state.ARRAY[open_cfw_gx8002_power_state.COUNT],record,sizeof(*record)); \
    ++open_cfw_gx8002_power_state.COUNT; \
    return 0; \
}
REGISTER(open_cfw_gx8002_register_suspend,suspend,suspend_count)
REGISTER(open_cfw_gx8002_register_resume,resume,resume_count)
