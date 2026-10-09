/* Reconstructed from authenticated stock instructions, UART-domain subset. */
#include "providers.h"
#include "../../foundation/power_domain/power_domain.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
/* Full-width argument is narrowed by stock before descriptor lookup. This
 * reconstruction only claims UART rows11..14, not all predicate groups. */
uint32_t uart_group_can_poll(uint32_t domain) {
    opencfw_power_domain_descriptor_t d;
    if(opencfw_power_domain_descriptor(&d,(uint8_t)domain)) return 1;
    if(d.status_mask!=0x1e00) return 1; /* other groups outside validated subset */
    if((W(d.enable_register)&0x1e00) && !(W(d.enable_register)&d.enable_mask)) return 0;
    return 1;
}
uint32_t uart_power_pre(void) {
    volatile uint32_t *slot=(volatile uint32_t *)0x2007327c;
    if(!*slot)return 0;
    return ((uint32_t (*)(void))(uintptr_t)*slot)();
}
uint32_t uart_power_post(void) {
    volatile uint32_t *slot=(volatile uint32_t *)0x20073280;
    if(!*slot)return 0;
    return ((uint32_t (*)(void))(uintptr_t)*slot)();
}
uint32_t uart_group_control(uint32_t action,uint32_t enable,void *metadata) {
    volatile uint32_t *slot=(volatile uint32_t *)0x20073274;
    if(!*slot)return 0;
    return ((uint32_t (*)(uint32_t,uint32_t,void *))(uintptr_t)*slot)((uint8_t)action,(uint8_t)enable,metadata);
}
extern void uart_delay_boundary(uint32_t);
uint32_t uart_status_wait(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected,uint32_t equal) {
    for(;;){
        uint32_t matched=(W(address)&mask)==expected;
        if((uint8_t)equal ? matched : !matched)return 0;
        if(!budget--)return 4;
        uart_delay_boundary(1);
    }
}
