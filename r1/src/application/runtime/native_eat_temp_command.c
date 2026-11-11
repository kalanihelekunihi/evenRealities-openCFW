/* Stock 0x4f1c4: report the calibrated pair of temperature sensors. */
#include <stdint.h>

extern void r1_temperature_pair_reduce(volatile void *output);
extern void r1_eat_respond_format(const char *format, ...);

static int16_t read_signed16(const uint8_t *data)
{
    return (int16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

void r1_eat_callback_0004f1c4(char *argument)
{
    (void)argument;
    uint8_t sample[8] = {0};
    r1_temperature_pair_reduce(sample);
    const int32_t temp0 = read_signed16(sample + 1);
    const int32_t temp2 = read_signed16(sample + 3);
    r1_eat_respond_format(
        "TEMP: sensor_cnt=%d, temp0=%d, temp2=%d, avg=%d (unit: 0.001C)\r\n",
        sample[0], temp0, temp2, (temp0 + temp2) / 2);
}
