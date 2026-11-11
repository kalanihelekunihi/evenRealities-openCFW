/* Stock 0x6778c: native numerical score over the 19-float statistics record. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern double r1_native_tanh(double);
extern float r1_native_powf(float,float);

float r1_gomore_sleep_score_native(const volatile void *metrics)
{
    float score=0.0f;
    (void)gomore_primitives_sleep_score(
        (const gomore_primitives_sleep_statistics *)(uintptr_t)metrics,
        r1_native_tanh,r1_native_powf,&score);
    return score;
}
