/* Stock 0x4f4a4: report the YHM VPMIC current-sense ADC voltage. */
#include <stdint.h>

extern uint32_t r1_battery_voltage_read(void);
extern void r1_eat_respond_format(const char *format, ...);

void r1_eat_callback_0004f4a4(char *argument)
{
    (void)argument;
    const uint32_t millivolts = r1_battery_voltage_read();
    r1_eat_respond_format("pmic_isns_voltage:%d mv\r\n", millivolts);
}
