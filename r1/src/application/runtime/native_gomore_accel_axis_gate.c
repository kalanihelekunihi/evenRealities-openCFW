#include "native_gomore_accel_axis_gate.h"

static int32_t sample(uint32_t at)
{
    return *(volatile int16_t *)(uintptr_t)at;
}

uint32_t r1_gomore_accel_axis_gate_native(uint32_t x, uint32_t y, uint32_t z,
                                        uint32_t length, uint32_t cursor,
                                        uint32_t window, uint32_t primary,
                                        uint32_t secondary)
{
    uint32_t sums[3] = {0, 0, 0};
    uint8_t first[3] = {0, 0, 0}, second[3] = {0, 0, 0};
    for (uint32_t step = 1; (int32_t)step <= (int32_t)window; step++) {
        uint32_t position = cursor - step;
        if ((int32_t)position < 0) position += length;
        uint32_t offset = (uint32_t)(int32_t)(int8_t)position * 2u;
        int32_t a = sample(x + offset);
        int32_t b = sample(y + offset);
        int32_t c = sample(z + offset);
        sums[0] += (uint32_t)a;
        sums[1] += (uint32_t)b;
        sums[2] += (uint32_t)c;
        if (a > (int32_t)primary) first[0]++;
        if (a > (int32_t)secondary) second[0]++;
        if (b > (int32_t)primary) first[1]++;
        if (b > (int32_t)secondary) second[1]++;
        if (c > (int32_t)primary) first[2]++;
        if (c > (int32_t)secondary) second[2]++;
    }
    /* Native ranking starts from zero, keeps strict ties and may select axis 0
       twice when no positive sum enters either rank. */
    int32_t maximum = 0, runner_up = 0;
    uint32_t best = 0, next = 0;
    for (uint32_t axis = 0; axis < 3; axis++) {
        int32_t sum = (int32_t)sums[axis];
        if (sum > maximum) {
            runner_up = maximum;
            next = best;
            maximum = sum;
            best = axis;
        } else if (sum > runner_up) {
            runner_up = sum;
            next = axis;
        }
    }
    return (int8_t)first[best] >= 3 && (int8_t)second[next] >= 3
        ? 1u : UINT32_MAX;
}
