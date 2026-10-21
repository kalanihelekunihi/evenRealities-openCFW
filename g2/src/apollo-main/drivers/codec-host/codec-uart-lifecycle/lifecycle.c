#include "lifecycle.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t codec_hal_power(uint32_t,uint32_t,uint32_t);
extern uint32_t codec_gpio_config(uint32_t,uint32_t);
extern uint32_t codec_hal_configure(uint32_t,const uint32_t *);
void codec_ring_initialize(uart3_ring_t *q,uint8_t *storage,uint32_t size){
 /* Invalid non-power-of-two assertion path is deliberately outside contract. */
 q->storage=storage;q->mask=size-1;q->read=0;q->write=0;
}
void codec_rx_callback(const uint8_t *src,uint32_t count){uart3_ring_write((uart3_ring_t *)(uintptr_t)0x20073ed4,src,count);}
void codec_channel_callback(uint32_t channel,uint32_t callback){channel=(uint8_t)channel;if(channel<4&&callback)W(0x20000d2c+channel*28+20)=callback;}
uint32_t codec_channel_enable(uint32_t channel){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=0x20000d2c+channel*28;
 uint32_t status=codec_hal_power(W(d+4),0,1),pins=W(d+8);
 (void)codec_gpio_config(W(pins+4),W(pins+12));(void)codec_gpio_config(W(pins),W(pins+8));
 B(d+24)=1;return status;
}
uint32_t codec_channel_disable(uint32_t channel){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=0x20000d2c+channel*28,pins=W(d+8);
 B(d+24)=0;(void)codec_gpio_config(W(pins+4),3);(void)codec_gpio_config(W(pins),0xe083);
 return codec_hal_power(W(d+4),2,1);
}
uint32_t codec_channel_baud(uint32_t channel,uint32_t baud){
 channel=(uint8_t)channel;if(channel>=4)return 1;uint32_t d=0x20000d2c+channel*28;
 if(!B(d+24))return 1;
 uint32_t config[4];uint32_t ptr=W(d+12);for(unsigned i=0;i<4;i++)config[i]=W(ptr+4*i);
 config[0]=baud;return codec_hal_configure(W(d+4),config)==0?0:1;
}
int32_t codec_uart_initialize(void){
 if(!B(0x20075014)){
  codec_ring_initialize((uart3_ring_t *)(uintptr_t)0x20073ed4,(uint8_t *)(uintptr_t)0x200731b0,64);
  codec_channel_callback(3,(uint32_t)(uintptr_t)codec_rx_callback);B(0x20075014)=1;
 }
 if(B(0x20075015))return 0;
 if(codec_channel_enable(3)!=0)return -1;
 B(0x20075015)=1;return 0;
}
int32_t codec_uart_close(void){
 if(!B(0x20075015))return 0;
 if(codec_channel_disable(3)!=0)return -1;
 B(0x20075015)=0;return 0;
}
int32_t codec_uart_baud(uint32_t baud){return codec_channel_baud(3,baud);}
int32_t codec_host_initialize(void){int32_t r=codec_uart_initialize();if(r)return r;(void)codec_uart_baud(115200);return 0;}
