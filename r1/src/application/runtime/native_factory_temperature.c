/* Stock 0x3cd24. The temperature reducer supplies the first five bytes of
 * the record; the monitor discards both sample values but preserves loads. */
#include <stdint.h>
#include "native_factory_mode.h"
extern uint32_t r1_native_charger_state_get(void),r1_charge_state_byte_get(void);
extern void r1_temperature_pair_reduce(volatile void *);
extern void r1_kv_nv_r1_word_set_a(uint32_t),r1_kv_nv_r1_byte_set_a(uint32_t);
extern uint32_t r1_device_info_configuration_byte78_get(void),r1_factory_mode_stop(void);
typedef struct __attribute__((packed,may_alias)) {uint16_t value;} monitor_half;
void r1_temperature_sample_monitor(void)
{
    if(!r1_factory_mode_state.active)return;
    _Alignas(8) volatile uint8_t record[24];
    (void)r1_native_charger_state_get();
    (void)r1_charge_state_byte_get();
    r1_temperature_pair_reduce(record);
    (void)((const volatile monitor_half *)(record+1))->value;
    uint16_t sample=((const volatile monitor_half *)(record+3))->value;
    ((volatile monitor_half *)(record+16))->value=sample;
    uint32_t count=r1_factory_mode_state.configuration+1u;
    r1_factory_mode_state.configuration=count;
    uint32_t saved=r1_factory_mode_state.saved_configuration;
    if(count-saved>=5u){
        r1_factory_mode_state.saved_configuration=count;
        r1_kv_nv_r1_word_set_a(count);
    }
    if(r1_factory_mode_state.configuration>=240u){
        r1_kv_nv_r1_byte_set_a(r1_device_info_configuration_byte78_get()|16u);
        (void)r1_factory_mode_stop();
    }
}
