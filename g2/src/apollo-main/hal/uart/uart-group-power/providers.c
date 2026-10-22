/* Reconstructed from authenticated stock instructions, UART-domain subset. */
#include "providers.h"
#include "../../../../apollo-common/power-domain/power_domain.h"
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
/* uart_power_pre / uart_power_post / uart_group_control (stock 0x48032C /
 * 0x480342 / 0x480312) are upstream am_hal_spotmgr_tempco_postpone /
 * am_hal_spotmgr_tempco_pending_handle / am_hal_spotmgr_power_state_update
 * (payload defsym). */
extern void uart_delay_boundary(uint32_t);
uint32_t uart_status_wait(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected,uint32_t equal) {
    for(;;){
        uint32_t matched=(W(address)&mask)==expected;
        if((uint8_t)equal ? matched : !matched)return 0;
        if(!budget--)return 4;
        uart_delay_boundary(1);
    }
}
