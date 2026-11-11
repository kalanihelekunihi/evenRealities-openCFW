/* Stock 2adfc is exactly BX LR, not a missing algorithm provider. */
#include <stdint.h>
void r1_gsensor_sample_sink_nop(uint32_t timestamp, int32_t x,
                               int32_t y, int32_t z)
{
    (void)timestamp; (void)x; (void)y; (void)z;
}
