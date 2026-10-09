/* Reconstructed UART domains11..14 only; no general-peripheral replacement. */
#include <stdint.h>
#include "../uart_group_power_offline/providers.h"
#include "../../foundation/power_domain/power_domain.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t uart_save_irq(void){uint32_t old;__asm volatile("mrs %0, primask\n\tcpsid i":"=r"(old)::"memory");return old;}
static void restore(uint32_t old){__asm volatile("msr primask, %0"::"r"(old):"memory");}
uint32_t uart_peripheral_enable(uint32_t domain){
    domain=(uint8_t)domain;
    if(domain<11||domain>14)return 6; /* only bounded UART subset is claimed */
    opencfw_power_domain_descriptor_t d;
    uint32_t status=opencfw_power_domain_descriptor(&d,domain);if(status)return status;
    if(W(d.enable_register)&d.enable_mask)return 0;
    uart_power_pre();
    uart_group_control(3,1,&d.status_mask); /* callback return ignored */
    uint32_t old=uart_save_irq();W(d.enable_register)|=d.enable_mask;restore(old);
    uart_power_post();
    status=uart_status_wait(5,d.status_register,d.status_mask,d.status_mask,1);
    if(status)return status;
    return (W(d.status_register)&d.status_mask)?0:1;
}
uint32_t uart_peripheral_disable(uint32_t domain){
    domain=(uint8_t)domain;
    if(domain<11||domain>14)return 6;
    opencfw_power_domain_descriptor_t d;
    uint32_t status=opencfw_power_domain_descriptor(&d,domain);if(status)return status;
    if(!(W(d.enable_register)&d.enable_mask))return 0;
    uart_power_pre();uint32_t old=uart_save_irq();W(d.enable_register)&=~d.enable_mask;restore(old);
    if(uart_group_can_poll(domain)){
        status=uart_status_wait(5,d.status_register,d.status_mask,d.status_mask,0);
        if(!status)uart_group_control(3,0,&d.status_mask);
    }
    uart_power_post();return status;
}
