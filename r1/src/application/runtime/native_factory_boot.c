/* Stock 0x48ba4 gates delayed factory entry; historical buffer-fill label was
 * misleading. Raw-stack configuration getter ABI remains a separate gate. */
#include <stdint.h>
extern uint32_t r1_device_info_configuration_byte78_get(void);
extern uint32_t r1_device_info_configuration_word74_get(void);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern void r1_factory_mode_start(uint32_t,uint32_t);
void r1_factory_delayed_mode_start(uint32_t argument)
{
    (void)argument;
    r1_factory_mode_start(UINT32_C(0xffff),0);
}
void r1_factory_boot_mode_schedule(void)
{
    uint32_t configuration=r1_device_info_configuration_byte78_get();
    (void)r1_device_info_configuration_word74_get();
    if ((configuration>>6)!=0 && !(configuration&0x10u))
        r1_native_delayed_schedule(r1_factory_delayed_mode_start,0,30720);
}
