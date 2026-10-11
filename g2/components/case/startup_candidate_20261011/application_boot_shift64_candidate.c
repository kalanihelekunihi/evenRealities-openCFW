/* SPDX-License-Identifier: MIT
 * CASE native 0x08000294/0x080002b4 unsigned 64-bit shift helpers.
 */
#include <stdint.h>

uint64_t case_boot_shift_left64(uint64_t value,uint32_t count)
{
    uint32_t lo=(uint32_t)value,hi=(uint32_t)(value>>32);
    if(count>=64u)return 0u;
    if(count>=32u){hi=lo<<(count-32u);lo=0u;}
    else if(count!=0u){hi=(hi<<count)|(lo>>(32u-count));lo<<=count;}
    return ((uint64_t)hi<<32)|lo;
}

uint64_t case_boot_shift_right64(uint64_t value,uint32_t count)
{
    uint32_t lo=(uint32_t)value,hi=(uint32_t)(value>>32);
    if(count>=64u)return 0u;
    if(count>=32u){lo=hi>>(count-32u);hi=0u;}
    else if(count!=0u){lo=(lo>>count)|(hi<<(32u-count));hi>>=count;}
    return ((uint64_t)hi<<32)|lo;
}
