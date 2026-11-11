#ifndef R1_GOODIX_NATIVE_ALGORITHM_STATE_H
#define R1_GOODIX_NATIVE_ALGORITHM_STATE_H
#include <stdint.h>
#include "gh3x2x_demo_algo_call.h"
struct r1_goodix_algorithm_memory {
    GU8 initialized;
    GU8 reserved[3];
    GU32 *pool;
    GU32 size;
};
extern volatile struct r1_goodix_algorithm_memory r1_goodix_algorithm_memory;
/* Share the frame owner already defined by native_algorithm_config.c. */
extern const STGh3x2xFrameInfo *const *volatile r1_goodix_algorithm_frame_table;
extern volatile uint32_t r1_goodix_algorithm_started;
extern volatile uint8_t r1_goodix_algorithm_initialized[20];
_Static_assert(sizeof(void *)==4,"native algorithm frame pointer words");
#endif
