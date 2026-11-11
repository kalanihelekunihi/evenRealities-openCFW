/* Stock charger-state decode and YHM byte commands, using the C status ABI. */
#include <stdint.h>
extern uint32_t r1_yhm_register_read_byte_native(uint32_t,uint8_t *);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
__attribute__((noinline)) uint32_t r1_yhm_register_write_byte_native(uint32_t reg,uint32_t value)
{
    volatile uint32_t word=value;
    return r1_yhm_register_write_native(reg,1,(const uint8_t *)(uintptr_t)&word);
}
__attribute__((noinline)) uint32_t r1_pmic_charge_status_decode(void)
{
    volatile uint32_t values[4]={0,0,0,0};
    (void)r1_yhm_register_read_byte_native(5,(uint8_t *)(uintptr_t)&values[1]);
    (void)r1_yhm_register_read_byte_native(6,(uint8_t *)(uintptr_t)&values[2]);
    (void)r1_yhm_register_read_byte_native(7,(uint8_t *)(uintptr_t)&values[3]);
    if ((*(volatile uint8_t *)&values[2]>>4)!=12) return 0;
    if ((*(volatile uint8_t *)&values[1]>>5)!=5) return 0;
    if (*(volatile uint8_t *)&values[3]&128u) return 0;
    (void)r1_yhm_register_read_byte_native(3,(uint8_t *)(uintptr_t)&values[0]);
    uint32_t value=*(volatile uint8_t *)&values[0];
    if (!(value&64u)) {
        value|=64u;
        *(volatile uint8_t *)&values[0]=(uint8_t)value;
        (void)r1_yhm_register_write_byte_native(3,value);
    }
    return 1;
}
__attribute__((noinline)) uint32_t r1_yhm_single_wire_command_native(void)
{
    volatile uint32_t word=0xf8;
    return r1_yhm_register_write_native(2,1,(const uint8_t *)(uintptr_t)&word);
}
uint32_t r1_yhm_single_wire_command_thunk(void)
{
    return r1_yhm_single_wire_command_native();
}
