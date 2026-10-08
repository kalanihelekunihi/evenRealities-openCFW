/* Independent command reconstruction; bounded sensor counts (widget1<=4,widget2<=1).
 * Reset entry is an explicit test boundary; no reset or flash is performed. */
#include "cy_scb_i2c.h"
#define CTX ((cy_stc_scb_i2c_context_t *)0x200008ecu)
#define RX ((uint8_t *)0x200009a0u)
#define TX ((uint8_t *)0x200009b0u)
static void arm_tx(void) { Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,TX,16,CTX); }
static void ack(uint8_t op,uint8_t status) { TX[0]=op;TX[1]=status;TX[2]=0x17;arm_tx(); }
static void sensor_read(unsigned widget,uint8_t *out) {
 uintptr_t base=*(uint32_t *)(0x200004ecu+12u);
 uintptr_t w=base+widget*0x90u;
 uintptr_t sensors=*(uint32_t *)(w+4u);
 unsigned count=*(uint16_t *)(w+0x38u);
 for(unsigned i=0;i<count;i++) { uint16_t v=*(uint16_t *)(sensors+i*10u+4u);out[i*2u]=(uint8_t)v;out[i*2u+1u]=(uint8_t)(v>>8); }
}
__attribute__((noinline,noreturn)) void touch_reset_boundary(void) { for(;;)__asm volatile("" ::: "memory"); }
void app_event(uint32_t events) {
 if(events & 0x20u) {
  uint8_t n=(uint8_t)CTX->slaveRxBufferIdx;
  if(!(events&0x40u) && (uint8_t)(n-1u)<16u && RX[0]<9u) {
   if(RX[0]==1u) {
    TX[0]=2;TX[1]=2;TX[2]=0;TX[3]=1;
    Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,TX,16,CTX);
   } else if(RX[0]==6u) {
    uint16_t v=*(uint16_t *)0x200009d4u;TX[0]=(uint8_t)v;TX[1]=(uint8_t)(v>>8);arm_tx();
   } else if(RX[0]==8u) {
    uint16_t v=*(uint16_t *)0x200009d6u;for(unsigned i=0;i<16;i++)TX[i]=0;TX[0]=(uint8_t)v;TX[1]=(uint8_t)(v>>8);arm_tx();
   } else if(RX[0]==5u) {
    *(uint8_t *)0x200009cfu=1;ack(5,0); /* stock logger is an actual return-zero leaf */
   } else if(RX[0]==7u) {
    uint16_t v=n>2u ? (uint16_t)(RX[1]|((uint16_t)RX[2]<<8)) : 0;
    if(v) { *(uint16_t *)0x200009d6u=v;*(uint16_t *)0x200004e8u=v;*(uint8_t *)0x200009ceu=1;*(uint8_t *)0x200009cdu=1;ack(7,0); }
    else ack(7,0xff);
   } else if(RX[0]==4u) {
    uint8_t report[10];for(unsigned i=0;i<10;i++)((volatile uint8_t *)report)[i]=0;sensor_read(1,report);sensor_read(2,report+8);
    for(unsigned i=0;i<10;i++)TX[i]=report[i];arm_tx();
   } else if(RX[0]==2u) {
    ack(2,0);*(volatile uint8_t *)0x20000000u=0;touch_reset_boundary();
   }
  }
  Cy_SCB_I2C_SlaveConfigWriteBuf(SCB1,RX,16,CTX);
 }
 if(events & 0x10u) {
  for(unsigned i=0;i<16;i++)TX[i]=0x5a;
  Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,TX,16,CTX);
  *(volatile uint32_t *)0x40040440u=1;
 }
}
