/* Native LV grid descriptor count 0x48d4d0 and weighted round 0x48ca18. */
#include <stdint.h>
uint32_t audio_uart_lv_grid_descriptor_count_48d4d0(const int32_t *descriptors)
{
    uint32_t count=0;
    while(descriptors[count]!=0x1fffffff)count++;
    return count;
}
int32_t audio_uart_lv_grid_weight_round_48ca18(int32_t numerator,int32_t denominator)
{
    return (int32_t)((uint32_t)numerator+(uint32_t)(denominator/2))/denominator;
}
