/* Independent5188/5528/5548. CDAC51bc remains explicit callback boundary. */
#include "generator.h"
void touch_frame_mask(uint32_t mask,uint32_t state,uint32_t *out){uint32_t a=out[0],b=out[1],c=out[2];out[0]=a&~mask;out[1]=b&~mask;out[2]=c&~mask;if(state&4)out[0]=a|mask;if(state&2)out[1]=b|mask;if(state&1)out[2]=c|mask;}
uint32_t touch_adjust_divider(uint8_t method,uint8_t clock,uint16_t divider){if((clock&3)==2)return (method==1 || method==10)?divider>>2:divider>>1;return divider;}
uint32_t touch_generate_sensor(uint32_t type,uint32_t slot,uint32_t *out,const uint8_t *context,touch_cdac_generator cdac){
 const uint8_t *internal=*(const uint8_t **)(context+8),*descriptor=(const uint8_t *)(*(const uint32_t *)(context+(type?52:48))+slot*4u);uint32_t id=*(const uint16_t *)descriptor;const uint8_t *w=(const uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*c=(const uint8_t *)(*(const uint32_t *)(context+16)+id*60u);uint32_t method=w[122];
 if(type==1){out[0]=(internal[96]&15u)|((internal[93]<<4)&255u)|((internal[94]<<8)&0xf00u)|(((uint32_t)*(const uint16_t *)(c+12)<<16)&0x3f0000u)|((uint32_t)internal[95]<<24);out[1]=*(const uint16_t *)(c+26)|((uint32_t)*(const uint16_t *)(c+28)<<16);out[2]=*(const uint16_t *)(c+8)|((c[32]<<16)&0x70000u)|(method==1?0:0x1000000u);out[3]=out[4]=0;out+=5;}else out[6]=(uint32_t)w[140]<<24;
 out[3]=(((uint32_t)(w[132]-1)<<14)&0x4000u)|((*(const uint16_t *)(c+44)-1u)&0x3fffu);if(c[52]==1 && slot!=*(const uint16_t *)(w+128))out[3]|=0x8000u;
 uint32_t status=cdac(descriptor,out,context);if(status)return status;if(method!=1)return 1;
 uint32_t divider=touch_adjust_divider((uint8_t)method,c[33],*(const uint16_t *)(c+14))-1u;out[5]=((divider<<16)&0x0fff0000u)|(((uint32_t)c[33]<<28)&0x30000000u)|((uint32_t)c[56]<<30)|3u;return 0;
}
/* Independent51bc..52b6. Bit12 is calibration-single mode in comparator SDK. */
uint32_t touch_generate_cdac(const uint8_t *descriptor,uint32_t *out,const uint8_t *context){
 uint32_t id=*(const uint16_t *)descriptor,sensor=*(const uint16_t *)(descriptor+2);const uint8_t *w=(const uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*runtime=(const uint8_t *)(*(const uint32_t *)(context+16)+id*60u),*internal=*(const uint8_t **)(context+8),*c=*(const uint8_t **)w;uint32_t divider=*(const uint16_t *)(runtime+54);if(divider)divider--;out[3]|=(divider<<16)&0x0fff0000u;
 uint32_t method=w[122],value=0x00400000u;if((method==1 && internal[90]==1) || (method==2 && internal[91]==1) || (method==10 && internal[92]==1))value=0x00c00000u|(((uint32_t)c[51]<<28)&0x70000000u);
 if(!(*(const uint32_t *)(*(const uint8_t **)(context+4)+8)&0x1000u)){
  uint32_t row=method==1 && sensor>=w[58];value|=c[row?47:46];value|=((uint32_t)c[row?49:48]<<16)&0x001f0000u;if(method==1)value|=(uint32_t)(*(const uint8_t **)(w+4))[sensor*10+9]<<8;
 }
 out[4]=value;return 0;
}
uint32_t touch_generate_sensor_closed(uint32_t type,uint32_t slot,uint32_t *out,const uint8_t *context){return touch_generate_sensor(type,slot,out,context,touch_generate_cdac);}
