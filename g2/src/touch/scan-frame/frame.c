/* Independent MSCLP register-frame loaders9178/6928; volatile bus ordering. */
#include <stdint.h>
#include "frame.h"
void touch_load_scan_frame(volatile uint32_t *hw,uint32_t mode,const uint32_t *frame){
 uint32_t start=1;
 if(mode==5){hw[0x3020/4]=0;start=0;}
 else if(mode==11){for(uint32_t j=0;j<5;j++)hw[(0x3000/4)+j]=frame[j];hw[0x3020/4]=frame[5];start=6;}
 else hw[0x3020/4]=frame[0];
 for(uint32_t j=0;j<5;j++)hw[(0x3024/4)+j]=frame[start+j];
}
void touch_start_scan_frame(const uint32_t *frame,const uint8_t *context){
 const uint8_t *common=*(const uint8_t **)context;volatile uint32_t *hw=**(volatile uint32_t *const *const *)(common+8);
 hw[0]|=0x80000000u;hw[0x120/4]=0x01110011u;(void)hw[0x120/4];hw[0x100/4]=0xc1011111u;(void)hw[0x100/4];touch_load_scan_frame(hw,6,frame);
 hw[0x3034/4]|=6u;hw[0x3034/4]|=1u;hw[0x3800/4]=1;
}
