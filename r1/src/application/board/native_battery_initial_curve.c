#include <stdint.h>
extern uint32_t r1_batcfg_byte0_get(void);
/* Native immutable records0x99ef6..0x9a0d5: product voltage calibration,
 * structured as lower/upper millivolts and interval weight, not code. */
typedef struct { uint16_t lower,upper; uint8_t weight,reserved; } r1_initial_charge_interval;
_Static_assert(sizeof(r1_initial_charge_interval)==6,"native calibration stride");
__attribute__((section(".r1.battery.initial_charge_tables"),used))
const r1_initial_charge_interval r1_battery_initial_charge_tables[4][20]={
    {
        {3350,3799,5,0},
        {3799,3848,5,0},
        {3848,3887,5,0},
        {3887,3918,5,0},
        {3918,3940,5,0},
        {3940,3960,5,0},
        {3960,3978,5,0},
        {3978,3999,5,0},
        {3999,4021,5,0},
        {4021,4048,5,0},
        {4048,4078,5,0},
        {4078,4112,5,0},
        {4112,4152,5,0},
        {4152,4200,5,0},
        {4200,4250,5,0},
        {4250,4303,5,0},
        {4303,4320,5,0},
        {4320,4330,5,0},
        {4330,4340,5,0},
        {4340,4310,5,0},
    },
    {
        {3350,3784,5,0},
        {3784,3809,5,0},
        {3809,3845,5,0},
        {3845,3871,5,0},
        {3871,3885,5,0},
        {3885,3898,5,0},
        {3898,3913,5,0},
        {3913,3933,5,0},
        {3933,3956,5,0},
        {3956,3983,5,0},
        {3983,4013,5,0},
        {4013,4043,5,0},
        {4043,4074,5,0},
        {4074,4121,5,0},
        {4121,4167,5,0},
        {4167,4211,5,0},
        {4211,4261,5,0},
        {4261,4318,5,0},
        {4318,4330,5,0},
        {4330,4350,5,0},
    },
    {
        {3350,3799,5,0},
        {3799,3848,5,0},
        {3848,3887,5,0},
        {3887,3918,5,0},
        {3918,3940,5,0},
        {3940,3960,5,0},
        {3960,3978,5,0},
        {3978,3999,5,0},
        {3999,4021,5,0},
        {4021,4048,5,0},
        {4048,4078,5,0},
        {4078,4112,5,0},
        {4112,4152,5,0},
        {4152,4200,5,0},
        {4200,4250,5,0},
        {4250,4303,5,0},
        {4303,4320,5,0},
        {4320,4330,5,0},
        {4330,4340,5,0},
        {4340,4350,5,0},
    },
    {
        {3350,3784,5,0},
        {3784,3809,5,0},
        {3809,3845,5,0},
        {3845,3871,5,0},
        {3871,3885,5,0},
        {3885,3898,5,0},
        {3898,3913,5,0},
        {3913,3933,5,0},
        {3933,3956,5,0},
        {3956,3983,5,0},
        {3983,4013,5,0},
        {4013,4043,5,0},
        {4043,4074,5,0},
        {4074,4121,5,0},
        {4121,4167,5,0},
        {4167,4211,5,0},
        {4211,4261,5,0},
        {4261,4318,5,0},
        {4318,4330,5,0},
        {4330,4350,5,0},
    },
};
/* The first table ends with a descending interval in the locked image.
 * Preserve its4310 upper clamp; do not repair product calibration data. */
uint32_t r1_battery_charging_initial_curve(uint32_t voltage)
{
    uint32_t kind=r1_batcfg_byte0_get();
    const r1_initial_charge_interval *table=r1_battery_initial_charge_tables[(kind>=1u && kind<=3u) ? kind-1u:3u];
    if (voltage<2400u) return 50;
    if (voltage<table[0].lower) voltage=table[0].lower;
    if (voltage>table[19].upper) voltage=table[19].upper;
    for (uint32_t i=0;i<20;i++) {
        if (voltage<=table[i].upper) {
            uint8_t sum=0;
            for (uint32_t j=0;j<i;j++) sum=(uint8_t)(sum+table[j].weight);
            uint32_t denominator=(uint16_t)(table[i].upper-table[i].lower);
            if (!denominator) return sum;
            uint32_t numerator=(voltage-table[i].lower)*table[i].weight;
            return (uint8_t)(numerator/denominator+sum);
        }
    }
    return 50;
}
