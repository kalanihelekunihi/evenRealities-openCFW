/* Stock 0x2000673c: EAT stream handles, in HR/SPO2/TEMP/HRV/ACC order. */
#include <stdint.h>

volatile uint32_t r1_eat_stream_handles[5];

extern void r1_sensor_stream_unregister_by_name(const char *name,
                                                uint32_t handle);
extern uint32_t r1_sensor_stream_register_by_name(const char *name,
                                                 const char *group,
                                                 uintptr_t callback,
                                                 uint32_t order,
                                                 uint32_t flags);
extern void r1_factory_heart_rate_diagnostic_plan(uint32_t, void *);
extern void r1_factory_spo2_diagnostic_plan(uint32_t, void *);
extern void r1_factory_temperature_diagnostic_plan(uint32_t, void *);
extern void r1_factory_hrv_diagnostic_plan(uint32_t, void *);
extern void r1_factory_acc_diagnostic_plan_decode(uint32_t, void *);

static void open_stream(uint32_t slot, const char *name, uintptr_t callback)
{
    if (r1_eat_stream_handles[slot] == 0u) {
        r1_eat_stream_handles[slot] = r1_sensor_stream_register_by_name(
            name, "at", callback, 1u, 1u);
    }
}

static void close_stream(uint32_t slot, const char *name)
{
    const uint32_t handle = r1_eat_stream_handles[slot];
    if (handle != 0u) {
        r1_sensor_stream_unregister_by_name(name, handle);
        r1_eat_stream_handles[slot] = 0u;
    }
}

void r1_eat_callback_0004f2bc(char *argument)
{
    (void)argument;
    close_stream(0u, "hr");
}

void r1_eat_callback_0004f8bc(char *argument)
{
    (void)argument;
    close_stream(1u, "spo2");
}

void r1_eat_callback_0004f928(char *argument)
{
    (void)argument;
    close_stream(2u, "temp");
}

void r1_eat_callback_0004f328(char *argument)
{
    (void)argument;
    close_stream(3u, "hrv");
}

void r1_eat_callback_0004ed14(char *argument)
{
    (void)argument;
    close_stream(4u, "acc");
}

void r1_eat_callback_0004f2dc(char *argument)
{
    (void)argument;
    open_stream(0u, "hr", (uintptr_t)r1_factory_heart_rate_diagnostic_plan);
}

void r1_eat_callback_0004f8e0(char *argument)
{
    (void)argument;
    open_stream(1u, "spo2", (uintptr_t)r1_factory_spo2_diagnostic_plan);
}

void r1_eat_callback_0004f94c(char *argument)
{
    (void)argument;
    open_stream(2u, "temp", (uintptr_t)r1_factory_temperature_diagnostic_plan);
}

void r1_eat_callback_0004f348(char *argument)
{
    (void)argument;
    open_stream(3u, "hrv", (uintptr_t)r1_factory_hrv_diagnostic_plan);
}

void r1_eat_callback_0004ed34(char *argument)
{
    (void)argument;
    open_stream(4u, "acc", (uintptr_t)r1_factory_acc_diagnostic_plan_decode);
}
