/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Recovered range callback; all arithmetic follows target uint32 wrap. */
struct open_cfw_range_state { uint32_t limit; void *handle; };
extern struct open_cfw_range_state open_cfw_gx8002_range_state;
extern int open_cfw_gx8002_submit_range(void *handle,const uint32_t range[2]);
int open_cfw_gx8002_next_range(uint32_t first,uint32_t last)
{
    uint32_t range[2]={last+1,last-first+1+last};
    if (range[1]>=open_cfw_gx8002_range_state.limit) {
        range[0]=0;
        range[1]=last-first;
    }
    return open_cfw_gx8002_submit_range(open_cfw_gx8002_range_state.handle,range);
}
