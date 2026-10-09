/* Reconstructed offline source interfaces; not a production HAL. */
#ifndef UART_GROUP_POWER_H
#define UART_GROUP_POWER_H
#include <stdint.h>
uint32_t uart_group_can_poll(uint32_t domain);
uint32_t uart_power_pre(void);
uint32_t uart_power_post(void);
uint32_t uart_group_control(uint32_t action,uint32_t enable,void *metadata);
uint32_t uart_status_wait(uint32_t budget,uint32_t address,uint32_t mask,uint32_t expected,uint32_t equal);
#endif
