/* Independent initialization fields4c84..4d8e, before mode/capture calls. */
#include "mode.h"
uint32_t touch_cap_init_fields(uint8_t *c){
 if(!c)return 1;uint8_t *i=*(uint8_t **)(c+8),*w=**(uint8_t ***)(c+12);const uint8_t *common=*(const uint8_t **)c;
 i[116]=i[117]=0;*(uint32_t *)i=*(uint32_t *)(i+4)=*(uint32_t *)(i+8)=*(uint32_t *)(i+12)=0;
 for(uint32_t n=0;n<3;n++)w[n*60+35]|=6;
 *(uint32_t *)(i+28)=0;*(uint32_t *)(i+44)=0x28f;*(uint32_t *)(i+20)=0;i[76]=0;i[87]=common[47];i[88]=common[45];i[89]=common[49];*(uint16_t *)(i+48)=*(const uint16_t *)(common+22);*(uint16_t *)(i+50)=*(const uint16_t *)(common+24);i[83]=common[52];i[84]=common[53];*(uint16_t *)(i+60)=0x84c;i[78]=0;i[79]=255;i[80]=142;i[81]=1;
 for(uint32_t n=0;n<3;n++){uint8_t *q=w+n*60;if(!*(uint16_t *)(q+4))q[35]|=8;if(!*(uint16_t *)(q+6))q[35]|=16;}
 *(uint16_t *)(i+64)=*(const uint16_t *)(common+30);*(uint16_t *)(i+62)=*(const uint16_t *)(common+28);*(uint16_t *)(i+68)=*(const uint16_t *)(common+34);*(uint16_t *)(i+66)=*(const uint16_t *)(common+32);i[114]=1;i[77]=3;i[90]=1;i[91]=i[92]=0;i[93]=6;i[94]=4;i[95]=10;i[96]=1;*(uint32_t *)(i+36)=0xf424;*(uint16_t *)(i+74)=32;return 0;
}
