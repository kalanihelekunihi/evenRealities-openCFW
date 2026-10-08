/* Independent reconstruction of the bounded paths of stock callback3700.
 * Test precondition: command0,1,3 or >=9; other valid command handlers remain
 * outside this module. This is not a complete firmware callback replacement. */
#include "cy_scb_i2c.h"
#define CTX ((cy_stc_scb_i2c_context_t *)0x200008ecu)
#define RX ((uint8_t *)0x200009a0u)
#define TX ((uint8_t *)0x200009b0u)
void app_event(uint32_t events) {
 if(events & 0x20u) {
  uint8_t n=(uint8_t)CTX->slaveRxBufferIdx;
  if(!(events&0x40u) && (uint8_t)(n-1u)<16u && RX[0]<9u) {
   if(RX[0]==1u) {
    TX[0]=2;TX[1]=2;TX[2]=0;TX[3]=1;
    Cy_SCB_I2C_SlaveConfigReadBuf(SCB1,TX,16,CTX);
   } else if(RX[0]!=0u && RX[0]!=3u) {
    *(volatile uint32_t *)0x20007000u=RX[0];return;
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
