/* Native Apollo Main 0x4ad9e2 reads word +4 from the stock ALS curve table
 * at 0x00730e24. The authenticated table's first entry is {10, 35}. */
#include <stdint.h>

uint32_t audio_als_first_curve_percent_4ad9e2(void)
{
    return 35u;
}
