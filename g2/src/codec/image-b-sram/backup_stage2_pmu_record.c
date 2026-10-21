/* Native cold PMU setup clears exactly 144 bytes at 0x2002cb88. Warm
 * startup replays callbacks from the retained record without reinitializing. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_pmu_record_2002cb88[36]
    __attribute__((section(".bss.image_b_pmu_record"), used, aligned(4)));
