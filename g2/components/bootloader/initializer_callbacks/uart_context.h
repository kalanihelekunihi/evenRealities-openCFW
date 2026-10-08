/* Reconstructed locked bootloader UART interfaces, not upstream HAL source. */
#ifndef OPENCFW_BOOT_UART_CONTEXT_H
#define OPENCFW_BOOT_UART_CONTEXT_H
#include <stdint.h>
typedef struct { uint32_t flags; uint8_t retained[280]; } opencfw_boot_uart_context;
_Static_assert(sizeof(opencfw_boot_uart_context)==0x11c,"locked UART stride");
extern volatile opencfw_boot_uart_context opencfw_boot_uart_context_pool[4];
uint32_t opencfw_bl_post_context_register(uint32_t module, const void *output);
uint32_t opencfw_bl_post_activate(uint32_t context,uint32_t tx,uint32_t tx_capacity,uint32_t rx,uint32_t rx_capacity);
uint32_t opencfw_bl_post_validate(uint32_t context,uint32_t config);
uint32_t opencfw_bl_post_finish(uint32_t context,uint32_t mask);
uint32_t opencfw_boot_uart_interrupt_clear(uint32_t context,uint32_t mask);
uint32_t opencfw_boot_uart_baud(uint32_t module,uint32_t baud,uint32_t *actual);
uint32_t opencfw_bl_post_enable(uint32_t irq);
uint32_t opencfw_bl_post_precommit(uint32_t irq);
uint32_t opencfw_bl_register_mode(uint32_t irq,uint32_t priority);
#endif
