#include <stdint.h>
extern uint32_t r1_batcfg_byte0_get(void);
extern volatile uint8_t r1_battery_device_context[];
/* Native immutable records0x99d16..0x99ef5: product voltage calibration,
 * structured as lower/upper millivolts and interval weight, not code. */
typedef struct { uint16_t lower,upper; uint8_t weight,reserved; } r1_discharge_interval;
_Static_assert(sizeof(r1_discharge_interval)==6,"native calibration stride");
__attribute__((section(".r1.battery.discharge_tables"),used))
const r1_discharge_interval r1_battery_discharge_tables[4][20]={
    {
        {3350,3622,5,0},
        {3622,3668,5,0},
        {3668,3682,5,0},
        {3682,3714,5,0},
        {3714,3742,5,0},
        {3742,3769,5,0},
        {3769,3795,5,0},
        {3795,3820,5,0},
        {3820,3845,5,0},
        {3845,3874,5,0},
        {3874,3902,5,0},
        {3902,3928,5,0},
        {3928,3978,5,0},
        {3978,4027,5,0},
        {4027,4077,5,0},
        {4077,4128,5,0},
        {4128,4175,5,0},
        {4175,4223,5,0},
        {4223,4262,5,0},
        {4262,4310,5,0},
    },
    {
        {3350,3609,5,0},
        {3609,3669,5,0},
        {3669,3683,5,0},
        {3683,3713,5,0},
        {3713,3742,5,0},
        {3742,3769,5,0},
        {3769,3792,5,0},
        {3792,3816,5,0},
        {3816,3844,5,0},
        {3844,3870,5,0},
        {3870,3902,5,0},
        {3902,3928,5,0},
        {3928,3977,5,0},
        {3977,4032,5,0},
        {4032,4077,5,0},
        {4077,4127,5,0},
        {4127,4177,5,0},
        {4177,4225,5,0},
        {4225,4265,5,0},
        {4265,4310,5,0},
    },
    {
        {3350,3531,5,0},
        {3531,3653,5,0},
        {3653,3676,5,0},
        {3676,3704,5,0},
        {3704,3725,5,0},
        {3725,3742,5,0},
        {3742,3758,5,0},
        {3758,3776,5,0},
        {3776,3797,5,0},
        {3797,3822,5,0},
        {3822,3850,5,0},
        {3850,3885,5,0},
        {3885,3926,5,0},
        {3926,3965,5,0},
        {3965,4024,5,0},
        {4024,4071,5,0},
        {4071,4124,5,0},
        {4124,4179,5,0},
        {4179,4241,5,0},
        {4241,4310,5,0},
    },
    {
        {3350,3609,5,0},
        {3609,3653,5,0},
        {3653,3677,5,0},
        {3677,3703,5,0},
        {3703,3721,5,0},
        {3721,3739,5,0},
        {3739,3755,5,0},
        {3755,3774,5,0},
        {3774,3796,5,0},
        {3796,3821,5,0},
        {3821,3852,5,0},
        {3852,3889,5,0},
        {3889,3926,5,0},
        {3926,3967,5,0},
        {3967,4026,5,0},
        {4026,4070,5,0},
        {4070,4120,5,0},
        {4120,4172,5,0},
        {4172,4232,5,0},
        {4232,4310,5,0},
    },
};
uint32_t r1_battery_discharge_curve(uint32_t voltage,uint32_t timestamp)
{
    (void)timestamp; /* Native does not consume its caller's second word. */
    uint32_t kind=r1_batcfg_byte0_get();
    if (voltage<2400u) return 50;
    const r1_discharge_interval *table=r1_battery_discharge_tables[(kind>=1u && kind<=3u) ? kind-1u:3u];
    if (voltage<table[0].lower) voltage=table[0].lower;
    if (voltage>table[19].upper) voltage=table[19].upper;
    for (uint32_t i=0;i<20;i++) {
        if (voltage<=table[i].upper) {
            uint8_t sum=0;
            for (uint32_t j=0;j<i;j++) sum=(uint8_t)(sum+table[j].weight);
            int32_t numerator=(int32_t)((voltage-table[i].lower)*table[i].weight);
            int32_t denominator=(int32_t)((uint32_t)table[i].upper-table[i].lower);
            uint32_t result=(uint8_t)(numerator/denominator+sum);
            if (voltage>4340u && r1_battery_device_context[46]>4u) result=100;
            return result;
        }
    }
    return 50;
}
