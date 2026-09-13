/* SPDX-License-Identifier: MIT */
/* Recovered stock wrapper. Unlike pinned upstream, the minor pass requires
 * a nonzero major-pass return as well as active state. */
#include <stdint.h>
extern int open_cfw_gx8002_max_score(void *context, int major);
extern uint32_t open_cfw_gx8002_max_window_index;
extern int open_cfw_gx8002_max_decoder_state;
extern void *KwsStragegyRun(void *context);
extern void KwsStrategyClearThresholdOffset(void);
extern void KwsStrategyReset(void);
int open_cfw_gx8002_max_decoder(void *context)
{
    int result = open_cfw_gx8002_max_score(context, 1);
    if (result && open_cfw_gx8002_max_decoder_state == 1)
        open_cfw_gx8002_max_score(context, 0);
    open_cfw_gx8002_max_window_index++;
    const unsigned char *activation = KwsStragegyRun(context);
    if (activation) {
        ((unsigned char *)context)[13] = activation[4];
        KwsStrategyClearThresholdOffset();
        KwsStrategyReset();
    }
    return 0;
}
