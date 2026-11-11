/* Stock EAT stream sample reporters registered by the five open commands. */
#include <stdint.h>

extern void r1_eat_respond_format(const char *format, ...);

static uint16_t read16(const uint8_t *data)
{
    return (uint16_t)data[0] | ((uint16_t)data[1] << 8);
}

void r1_factory_heart_rate_diagnostic_plan(uint32_t source, void *payload)
{
    (void)source;
    const uint8_t *const data = payload;
    r1_eat_respond_format("heartrate:%d\n", data[0], data[1], data[2]);
}

void r1_factory_spo2_diagnostic_plan(uint32_t source, void *payload)
{
    (void)source;
    const uint8_t *const data = payload;
    r1_eat_respond_format("spo2:%d\n", data[0]);
}

void r1_factory_hrv_diagnostic_plan(uint32_t source, void *payload)
{
    (void)source;
    const uint8_t *const data = payload;
    r1_eat_respond_format("hrv:%d,%d,%d,%d\n", read16(data), read16(data + 2),
                          read16(data + 4), read16(data + 6));
}

void r1_factory_temperature_diagnostic_plan(uint32_t source, void *payload)
{
    (void)source;
    uint8_t *const data = payload;
    const uint16_t quotient = read16(data) / 100u;
    data[0] = (uint8_t)quotient;
    data[1] = (uint8_t)(quotient >> 8);
    const int16_t signed_quotient = (int16_t)quotient;
    r1_eat_respond_format("temp:%d.%d\n", signed_quotient / 10,
                          signed_quotient % 10);
}

void r1_factory_acc_diagnostic_plan_decode(uint32_t source, void *payload)
{
    (void)source;
    const uint8_t *const data = payload;
    const uint16_t count = read16(data + 0xb4);
    for (uint8_t index = 0u; index < count; ++index) {
        if (index % 5u == 0u) {
            const uint8_t *const sample = data + 6u * index;
            r1_eat_respond_format("[%d],accx:%d, accy:%d, accz:%d\n",
                                  index, (int16_t)read16(sample),
                                  (int16_t)read16(sample + 2),
                                  (int16_t)read16(sample + 4));
        }
    }
    r1_eat_respond_format("==========\n");
}
