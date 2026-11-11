/* Locked G2 f89a4c46 elog UART output. The UART transfer path below it is
 * upstream AmbiqSuite 5.0.0 am_hal_uart.c. */
#include <stdint.h>
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern void opencfw_boot_delay_raw(uint32_t);
extern void *memset(void *,int,size_t);
extern uint32_t am_hal_uart_transfer(uint32_t handle,uint32_t descriptor); /* AmbiqSuite 5.0.0 */
NI uint32_t opencfw_boot_uart_log_send(uint32_t row,uint32_t borrowed,uint32_t length){
 uint32_t descriptor[14];memset(descriptor,0,sizeof descriptor);row=(uint8_t)row;uint32_t r=0x20000454+28*row;
 if(row>=4||B(r+24)!=1)return 1;
 descriptor[0]=borrowed;descriptor[1]=length;B(r+25)=0;
 uint32_t status=am_hal_uart_transfer(W(r+4),(uint32_t)(uintptr_t)descriptor);
 for(uint32_t i=0;i<1000&&B(r+25)!=1;i++)opencfw_boot_delay_raw(10);
 return status!=0;
}
extern uint32_t opencfw_boot_uart_log_send_ambient_abi(uint32_t borrowed,uint32_t length);
NI void opencfw_boot_elog_uart_output(const char *buffer,size_t length,uint32_t level){(void)level;(void)opencfw_boot_uart_log_send_ambient_abi((uint32_t)(uintptr_t)buffer,(uint32_t)length);}
