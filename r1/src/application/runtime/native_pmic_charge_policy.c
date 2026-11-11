/* Stock charge-event policy 0x96ad0 and delayed flag adapter 0x42d28. */
#include <stdint.h>
extern uint32_t r1_native_charger_state_get(void),r1_battery_voltage_get(void);
extern uint16_t r1_battery_raw_to_percent(void);
extern uint32_t r1_yhm_transport_release(void);
extern uint32_t r1_pmic_charge_status_decode(void),r1_yhm_block_word_set(uint32_t);
extern uint32_t r1_charge_state_byte_thunk(void),r1_device_info_configuration_byte78_get(void);
extern void r1_gxt310_temp_pair_read(volatile void *,volatile void *);
extern void r1_st25dvxxkc_bounded_mailbox_receive(volatile uint8_t *);
extern uint32_t r1_yhm_single_wire_command_thunk(void),r1_native_charger_ladder_set(float);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_battery_task_flags_set(uint32_t);
extern void r1_i2c5_nfc_resource_release(void);
extern uint32_t r1_pmic_event_op_dispatch(uint32_t),r1_charge_event_i2c_op(uint32_t);
extern uint32_t r1_pmic_post_device_callback_plan(uint32_t);
extern void r1_pmic_retry_callback_plan(uint32_t);
extern volatile uint8_t r1_nfc_charge_late_flag;
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
volatile uint32_t r1_pmic_charge_ladder_bits
 __attribute__((section(".r1.pmic.charge.ladder"),aligned(4)))=0;
const char r1_pmic_not_charged_ring[]="[RING]PMIC_CHARGED_NOT";
const char r1_pmic_not_charged_sdk[]="PMIC_CHARGED_NOT";
void r1_pmic_post_timer_callback_plan(uint32_t argument)
{
    (void)argument;
    (void)r1_battery_task_flags_set(8);
}
void r1_pmic_charge_event_plan(uint32_t event)
{
    uint32_t state=r1_native_charger_state_get();
    if (event!=0x5a)
        (void)r1_native_delayed_cancel(r1_pmic_post_timer_callback_plan,0);
    if (state==0) {
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x0c000000,r1_pmic_not_charged_ring,r1_pmic_not_charged_ring);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0003,r1_pmic_not_charged_sdk);
        r1_nfc_charge_late_flag=0xa5;
        (void)r1_native_delayed_cancel(r1_pmic_post_timer_callback_plan,0);
        r1_i2c5_nfc_resource_release();
        (void)r1_pmic_event_op_dispatch((uint32_t)(uintptr_t)r1_pmic_post_device_callback_plan);
        (void)r1_native_delayed_cancel(r1_pmic_retry_callback_plan,0);
        (void)r1_charge_event_i2c_op(0);
        (void)r1_battery_task_flags_set(0x10);
        (void)r1_yhm_block_word_set((uint32_t)(uintptr_t)r1_charge_event_i2c_op);
        return;
    }
    if ((state!=1 && state!=2)||event!=1) return;
    uint32_t voltage=r1_battery_voltage_get();
    uint32_t raw=r1_battery_raw_to_percent();
    (void)r1_yhm_transport_release();
    uint32_t status=r1_pmic_charge_status_decode();
    (void)r1_yhm_block_word_set(0);
    volatile uint16_t temperature0=0,temperature2=0;
    r1_gxt310_temp_pair_read(&temperature0,&temperature2);
    volatile uint8_t packet[24]={0};
    packet[1]=1;packet[2]=2;
    packet[3]=(uint8_t)r1_charge_state_byte_thunk();
    packet[4]=(uint8_t)((state&3u)|(((temperature0/1000u)&63u)<<2));
    packet[5]=(uint8_t)voltage;packet[6]=(uint8_t)(voltage>>8);
    packet[7]=(uint8_t)raw;packet[8]=(uint8_t)(raw>>8);
    packet[9]=(uint8_t)r1_device_info_configuration_byte78_get();
    packet[10]=(uint8_t)status;
    for (unsigned i=0;i<10;++i) packet[13+i]=(uint8_t)"2.2.6.0009"[i];
    r1_st25dvxxkc_bounded_mailbox_receive(packet);
    uint32_t temperature=packet[4]>>2;
    if (temperature>=45) {
        (void)r1_yhm_transport_release();
        (void)r1_yhm_single_wire_command_thunk();
        (void)r1_yhm_block_word_set(0);
        return;
    }
    uint32_t bits;
    if (temperature>=1 && temperature<15) bits=0x40808312;
    else if (temperature>=15) bits=0x4160f5c3;
    else return;
    if (r1_pmic_charge_ladder_bits==bits) return;
    union {uint32_t bits;float value;} setting={.bits=bits};
    r1_pmic_charge_ladder_bits=bits;
    (void)r1_native_charger_ladder_set(setting.value);
}
