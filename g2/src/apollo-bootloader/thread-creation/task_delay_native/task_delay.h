#include <stdint.h>
/* Scheduler ticks, not verified wall-clock milliseconds. */
int32_t opencfw_cmsis_delay(uint32_t ticks);
void opencfw_kernel_delay(uint32_t ticks);
