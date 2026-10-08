#include <stdint.h>
/* Authenticated transition-selection DATA at0x768BE0, not executable opcodes.
   Caller contract: profile next,old are in0..19; non-NULL output. */
static const uint8_t transition_data[28]={25,0,1,26,0,2,25,26,3,3,4,26,25,5,26,26,6,7,25,8,2,9,26,10,25,0,0,0};
uint32_t audio_platform_select(uint32_t next,uint32_t old,uint8_t *index) {
    *index=transition_data[5*(old>>2)+(next>>2)];
    if(*index==26) return 7;
    if(old==0 && next==8) *index=21;
    else if(old==8 && next==0) *index=22;
    if((old==8 && next==12)||(old==12 && next==8)) *index=23;
    if(*index!=25) return 0;
    if((old&3)!=0 && (old>>2)<5 && (next&3)==0 && (next>>2)<5) {
        *index=old==9 && next==8 ? 11 : old==1 && next==0 ? 12 : 24;
    } else if((old&3)==0 && (old>>2)<5 && (next&3)!=0 && (next>>2)<5) {
        *index=old==8 && next==9 ? 13 : old==0 && next==1 ? 14 : 24;
    } else if((old&3)>=2 && (old>>2)<5 && (next&3)<2 && (next>>2)<5) {
        *index=(old==2 && next==1)||(old==10 && next==9) ? 15 : 16;
    } else if((old&3)<2 && (old>>2)<5 && (next&3)>=2 && (next>>2)<5) {
        *index=old==9 && next==10 ? 17 : old==1 && next==2 ? 18 : 19;
    } else *index=(old==10 && next==11)||(old==11 && next==10) ? 20 : 24;
    return 0;
}
