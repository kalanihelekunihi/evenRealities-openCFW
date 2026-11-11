/* Stock 0x91174 registration and 0x3d818 recurring callback. Keep the raw
 * scheduler delay value; conversion and timer timing belong to that provider. */
#include <stdint.h>
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
void r1_battery_periodic_schedule_00091174(void);
void r1_battery_periodic_callback(uint32_t argument)
{
 (void)argument;
 (void)r1_battery_task_flags_set(0x20);
 /* A failed signal does not suppress the following registration. */
 r1_battery_periodic_schedule_00091174();
}
void r1_battery_periodic_schedule_00091174(void)
{
 r1_native_delayed_schedule(r1_battery_periodic_callback,0,0x7800);
}
