#include "lifecycle.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200731b0[] __asm__("g2_stock_ram_200731b0");
extern unsigned char g2ref_g2_stock_ram_20073ed0[] __asm__("g2_stock_ram_20073ed0");
extern unsigned char g2ref_g2_stock_ram_20075010[] __asm__("g2_stock_ram_20075010");
extern unsigned char g2ref_g2_uart_channels[] __asm__("g2_uart_channels");
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t codec_hal_power(uint32_t,uint32_t,uint32_t);
extern uint32_t codec_gpio_config(uint32_t,uint32_t);
extern uint32_t codec_hal_configure(uint32_t,const uint32_t *);
/* Retired 2026-10-30: the hand ring init was a copy of stock 0x598160 without its
 * power-of-two assert; 0x598160 is upstream ring_buffer_init, which callers now use (both
 * pass the constant size 64, so the assert never fires). */
/* Stock 0x58FB1C (codec UART3 RX ring write). The ring write it calls (stock
 * 0x5981C4) is upstream ring_buffer_queue_arr (third-party/upstream/ring-buffer);
 * uart3_ring_t has the ring_buffer_t layout {buffer, mask, tail, head}. */
extern void ring_buffer_queue_arr(void *buffer,const char *data,uint32_t size);
void codec_rx_callback(const uint8_t *src,uint32_t count){ring_buffer_queue_arr((uart3_ring_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073ed0+0x4u),(const char *)src,count);}
/* Stock 0x0055E8F0 (UART channel RX callback set) */
void codec_channel_callback(uint32_t channel,uint32_t callback){channel=(uint8_t)channel;if(channel<4&&callback)W(((uint32_t)(uintptr_t)g2ref_g2_uart_channels)+channel*28+20)=callback;}
/* Stock 0x0055E5BC (UART channel enable) */
uint32_t codec_channel_enable(uint32_t channel){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=(uint32_t)(uintptr_t)g2ref_g2_uart_channels+channel*28;
 uint32_t status=codec_hal_power(W(d+4),0,1),pins=W(d+8);
 (void)codec_gpio_config(W(pins+4),W(pins+12));(void)codec_gpio_config(W(pins),W(pins+8));
 B(d+24)=1;return status;
}
/* Stock 0x0055E630 (UART channel disable) */
uint32_t codec_channel_disable(uint32_t channel){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=(uint32_t)(uintptr_t)g2ref_g2_uart_channels+channel*28,pins=W(d+8);
 B(d+24)=0;(void)codec_gpio_config(W(pins+4),3);(void)codec_gpio_config(W(pins),0xe083);
 return codec_hal_power(W(d+4),2,1);
}
/* Stock 0x0055E898 (UART channel baud set) */
uint32_t codec_channel_baud(uint32_t channel,uint32_t baud){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=(uint32_t)(uintptr_t)g2ref_g2_uart_channels+channel*28;
 if(!B(d+24))return 1;
 uint32_t config[4];uint32_t ptr=W(d+12);for(unsigned i=0;i<4;i++)config[i]=W(ptr+4*i);
 config[0]=baud;return codec_hal_configure(W(d+4),config)==0?0:1;
}
int32_t codec_uart_initialize(void){
 if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x4u))){
  ring_buffer_init((uart3_ring_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073ed0+0x4u),(char *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200731b0),64);
  codec_channel_callback(3,(uint32_t)(uintptr_t)codec_rx_callback);B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x4u))=1;
 }
 if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x5u)))return 0;
 if(codec_channel_enable(3)!=0)return -1;
 B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x5u))=1;return 0;
}
int32_t codec_uart_close(void){
 if(!B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x5u)))return 0;
 if(codec_channel_disable(3)!=0)return -1;
 B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20075010+0x5u))=0;return 0;
}
/* Stock 0x58FAB6 (codec UART3 baud set) */
int32_t codec_uart_baud(uint32_t baud){return codec_channel_baud(3,baud);}
int32_t codec_host_initialize(void){int32_t r=codec_uart_initialize();if(r)return r;(void)codec_uart_baud(115200);return 0;}
