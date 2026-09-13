/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef struct { uint16_t gain; int16_t db; } output_gain;
_Static_assert(sizeof(output_gain)==4,"Gain mapping ABI");
/* Pinned NationalChip s_vol_table: explicit hardware code for each dB step.
 * These calibrated integer codes are not replaced by an approximate formula. */
const output_gain open_cfw_gx8002_aout_gain_steps[] = {
    {16,-18},{18,-17},{20,-16},{23,-15},{25,-14},{28,-13},
    {32,-12},{36,-11},{40,-10},{45,-9},{51,-8},{57,-7},
    {64,-6},{72,-5},{81,-4},{91,-3},{102,-2},{114,-1},
    {128,0},{144,1},{162,2},{181,3},{203,4},{228,5},
    {256,6},{288,7},{323,8},{362,9},{407,10},{460,11},
    {512,12},{576,13},{646,14},{725,15},{814,16},{913,17},{1023,18}
};
int open_cfw_gx8002_aout_set_db(void *handle, int16_t db)
{
    int clipped=db;
    if (clipped>18) clipped=18;
    if (clipped< -18) clipped=-18;
    uint32_t gain=open_cfw_gx8002_aout_gain_steps[clipped+18].gain;
    volatile uint32_t *reg=(volatile uint32_t *)0xa0b00014u;
    *reg=(*reg&~0x3ff0000u)|(gain<<16);
    /* Stock stores the caller's unclamped dB value. */
    *(volatile int16_t *)((uint8_t *)handle+18)=db;
    return 0;
}
int open_cfw_gx8002_aout_get_db(void *handle, volatile int16_t *db)
{
    uint32_t code=(*(volatile uint32_t *)0xa0b00014u>>16)&1023u;
    /* Stock reads adjacent table data on a miss, yielding1. Make that
     * compatibility result explicit without an out-of-bounds access. */
    int16_t mapped=1;
    for (unsigned i=0;i<37;i++) {
        if (open_cfw_gx8002_aout_gain_steps[i].gain==code) {
            mapped=(int16_t)((int)i-18);
            break;
        }
    }
    *db=mapped;
    return *(volatile int16_t *)((uint8_t *)handle+18);
}
