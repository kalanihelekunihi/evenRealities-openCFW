/* Stock 0x96a60: rearm before requesting the next PMIC retry action.
 * The delayed worker discards the callback result; use its ordinary void ABI. */
#include <stdint.h>
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern uint32_t r1_battery_task_flags_set(uint32_t);
void r1_pmic_retry_callback_plan(uint32_t argument)
{
    (void)argument;
    r1_native_delayed_schedule(r1_pmic_retry_callback_plan,0,0x199);
    (void)r1_battery_task_flags_set(4);
}
