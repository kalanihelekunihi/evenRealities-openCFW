/* Stock 0x4f4d4: persist power-off recovery state and signal power worker. */
#include <stdint.h>

extern uint32_t r1_battery_voltage_get(void);
extern uint32_t r1_time_backend_timestamp(void);
extern void r1_kv_dev_info_fields_set(volatile void *fields);
extern void *volatile r1_low_battery_thread_handle;
extern uint32_t osThreadFlagsSet(void *thread,uint32_t flags);
extern void r1_eat_respond_format(const char *format,...);

void r1_eat_callback_0004f4d4(char *argument)
{
    (void)argument;
    r1_eat_respond_format("at_pmic_power_off\r\n");
    volatile uint32_t fields[2]={0u,2u};
    const uint32_t millivolts=r1_battery_voltage_get();
    fields[1]=2u|((millivolts&0x3fffu)<<2);
    fields[0]=r1_time_backend_timestamp();
    r1_kv_dev_info_fields_set(fields);
    (void)osThreadFlagsSet(r1_low_battery_thread_handle,1u);
}
