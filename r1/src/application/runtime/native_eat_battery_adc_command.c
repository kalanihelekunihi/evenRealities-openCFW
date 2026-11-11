/* Stock 0x4ee18: report the current battery ADC and charge configuration. */
#include <stdint.h>

extern uint32_t r1_battery_voltage_get(void);
extern uint32_t r1_charge_state_byte_get(void);
extern uint32_t r1_batcfg_byte0_get(void);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004ee18(char *argument)
{
    (void)argument;
    const uint32_t millivolts = r1_battery_voltage_get();
    const uint32_t charge_state = r1_charge_state_byte_get();
    const uint32_t battery_type = r1_batcfg_byte0_get();
    r1_eat_respond_format("bat adc:%d mV, percent:%d, type:%d\r\n",
                          millivolts, charge_state, battery_type);
}
