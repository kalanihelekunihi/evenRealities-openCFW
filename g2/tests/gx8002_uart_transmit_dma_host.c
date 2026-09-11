/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdint.h>
#include "gx_dma_ahb.h"
static int selected, released, transferred, callbacks, bursts;
static GX_DMA_AHB_CH_CONFIG captured;
void open_cfw_gx8002_uart_transmit_complete(volatile uint32_t *d) {(void)d;}
void open_cfw_gx8002_dcache_clean_range(uint32_t b,uint32_t n) {assert(b==0x20050000 && n==32);}
int open_cfw_gx8002_dma_select(void) {return selected;}
void open_cfw_gx8002_dma_release(uint32_t c) {assert(c==3);released++;}
uint32_t open_cfw_gx8002_uart_dma_burst(volatile uint32_t *d,uint32_t tx) {(void)d;assert(tx==1);return ++bursts;}
void open_cfw_gx8002_dma_callback(int c,uint32_t cb,volatile uint32_t *d) {assert(c==3 && cb && d[31]==3);callbacks++;}
int open_cfw_gx8002_dma_transfer(uint32_t dst,uint32_t src,uint32_t n,int c,GX_DMA_AHB_CH_CONFIG *cfg) {assert(dst==0xa0000000 && src==0x20050000 && n==32 && c==3);captured=*cfg;transferred++;return -1;}
#include "runtime_gx8002_uart_transmit_dma.c"
int main(void) {
 for(unsigned p=0;p<4;p++) for(unsigned fail=0;fail<2;fail++) {
  volatile uint32_t d[32]={0};d[0]=p;d[1]=0xa0000000;d[31]=UINT32_MAX;
  selected=fail?-1:3;released=transferred=callbacks=bursts=0;
  int r=open_cfw_gx8002_uart_transmit_dma(d,0x20050000,32);
  if(fail) {assert(r==-1 && !released && !transferred && !bursts);}
  else if(p>1) {assert(r==-1 && released==1 && !transferred && !callbacks && d[31]==UINT32_MAX);}
  else {assert(r==0 && !released && transferred==1 && callbacks==1 && bursts==2);
   assert(captured.trans_width==0 && captured.src_msize==1 && captured.src_addr_update==0 && captured.src_hs_per==0 && captured.src_master_select==0 && captured.src_hs_select==0);
   assert(captured.dst_msize==2 && captured.dst_addr_update==1 && captured.dst_hs_per==(p?5:7) && captured.dst_master_select==1 && captured.dst_hs_select==0 && captured.flow_ctrl==1);
  }
 }
 return 0;
}
