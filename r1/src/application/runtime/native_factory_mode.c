/* Stock 0x48bd0. Only the observed 28-byte mode-state prefix is owned here.
 * Its native address 0x20006c34 is also read by the existing Goodix selector. */
#include <stdint.h>
#include <stddef.h>
#include "native_factory_mode.h"
extern uint32_t r1_device_info_configuration_byte78_get(void),r1_device_info_configuration_word74_get(void);
extern void r1_kv_nv_r1_byte_set_a(uint32_t),r1_kv_nv_r1_word_set_a(uint32_t);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_stream_timer_create_front(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_temperature_sample_monitor(void);
extern void r1_motion_sample_event_adapter(uint32_t,uint16_t *);
extern void r1_sensor_threshold_flag_latch(uint32_t,uint32_t *,uint32_t);
_Static_assert(sizeof(struct factory_state)==28,"observed native state prefix");
_Static_assert(offsetof(struct factory_state,timer)==16 && offsetof(struct factory_state,acc)==24,"native fields");
volatile struct factory_state r1_factory_mode_state __attribute__((section(".r1.factory.mode.state"),aligned(4)))={.reserved={0,0,0xff,0xff,0,0,0}};
void r1_factory_mode_start(uint32_t handle,uint32_t reset_configuration)
{
    (void)handle;
    if (r1_factory_mode_state.active) return;
    uint32_t configuration;
    if (reset_configuration) {
        uint32_t value=r1_device_info_configuration_byte78_get();
        r1_kv_nv_r1_byte_set_a(value|0xc0u);
        r1_factory_mode_state.configuration=0;
        r1_kv_nv_r1_word_set_a(0);
        configuration=r1_factory_mode_state.configuration;
    } else {
        configuration=r1_device_info_configuration_word74_get();
        r1_factory_mode_state.configuration=configuration;
    }
    r1_factory_mode_state.saved_configuration=configuration;
    r1_factory_mode_state.active=1;
    uint32_t timer=r1_factory_mode_state.timer;
    if (timer) (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
    r1_factory_mode_state.timer=r1_stream_timer_create_front((uint32_t)(uintptr_t)r1_temperature_sample_monitor,61440,0);
    if (!r1_factory_mode_state.acc)
        r1_factory_mode_state.acc=r1_sensor_stream_register_by_name("acc","factory",(uintptr_t)r1_motion_sample_event_adapter,1,0);
    if (!r1_factory_mode_state.aging)
        r1_factory_mode_state.aging=r1_sensor_stream_register_by_name("aging","factory",(uintptr_t)r1_sensor_threshold_flag_latch,1,0);
}
