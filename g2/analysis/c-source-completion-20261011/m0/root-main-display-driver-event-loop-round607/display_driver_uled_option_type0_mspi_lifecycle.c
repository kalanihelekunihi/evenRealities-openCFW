/* Apollo S200 MSPI wait, shutdown, and setup helpers. */
#include <stdint.h>

extern uint32_t display_driver_uled_wait_lower_538e8c(uint32_t);
extern void display_driver_uled_shutdown_lower_53909a(uint32_t,uint32_t);
extern void display_driver_uled_setup_lower_538d58(uint32_t,const void *,uint32_t *);

uint32_t display_driver_uled_mspi_wait_4bfd62(uint32_t *handle) {
    return display_driver_uled_wait_lower_538e8c(handle[0x20a]);
}

uint32_t display_driver_uled_mspi_shutdown_4bfc86(uint32_t *handle) {
    uint32_t module=handle[1];
    volatile uint32_t *saved=(volatile uint32_t *)(uintptr_t)
        (0x200523d8u+module*0x8d0u+0x828u);
    if (*saved!=0u) {
        display_driver_uled_shutdown_lower_53909a(*saved,1u);
        *saved=0u;
    }
    return 0u;
}

void display_driver_uled_mspi_setup_4bfc5a(uint32_t module,
                                             uint32_t half_parameter,
                                             uint32_t payload) {
    uint8_t args[12]={0};
    uint32_t half=half_parameter>>1;
    for (uint32_t i=0;i<4u;i++) {
        args[i]=(uint8_t)(half>>(8u*i));
        args[4u+i]=(uint8_t)(payload>>(8u*i));
    }
    args[8]=1u;
    uint32_t *saved=(uint32_t *)(uintptr_t)
        (0x200523d8u+module*0x8d0u+0x828u);
    display_driver_uled_setup_lower_538d58((module+8u)&255u,args,saved);
}
