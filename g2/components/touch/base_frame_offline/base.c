/* Independent register-frame reconstruction, locked touch ROM.
 * Typed constants are register configuration data at b41c/b470/b4c4,
 * not retained executable instructions. ARM32 coherent contexts only. */
#include "base.h"
static uint8_t *ptr(const uint8_t *c,unsigned off){return *(uint8_t *const *)(c+off);}
static uint16_t u16(const uint8_t *c,unsigned off){return *(const uint16_t *)(c+off);}
static const uint32_t default_modes[21] = {0x0u, 0x0u, 0x1000000u, 0x4001u, 0x87010100u, 0x53u, 0x5004u, 0x11000000u, 0x0u, 0x1000000u, 0x4001u, 0x87010000u, 0x52u, 0x5005u, 0x0u, 0x0u, 0x1000000u, 0x4001u, 0x87010000u, 0x51u, 0x5100u};
static const uint32_t dither_modes[21] = {0x0u, 0x763023u, 0x1000000u, 0x4001u, 0x87010100u, 0x53u, 0x5004u, 0x11000000u, 0x540045u, 0x1000000u, 0x4001u, 0x87010000u, 0x52u, 0x5005u, 0x0u, 0x542245u, 0x1000000u, 0x4001u, 0x87010000u, 0x51u, 0x5100u};
static const uint32_t pin_functions[14] = {0x41000000u, 0x40000000u, 0x1u, 0x8060000u, 0x7070000u, 0x402000au, 0x2040000u, 0x306u, 0x4020a00u, 0x9080000u, 0x40000100u, 0x4020303u, 0x4020404u, 0x4020000u};
void touch_generate_modes(uint8_t *c){
 uint8_t *i=ptr(c,8);uint32_t *m=(uint32_t *)(ptr(c,36)+144);
 for(unsigned j=0;j<21;j++)m[j]=default_modes[j];
 for(unsigned mode=0;mode<3;mode++)if(i[90+mode]==1)for(unsigned j=0;j<7;j++)m[7*mode+j]=dither_modes[7*mode+j];
 if(i[117]==5)m[11]|=0x100;
}
uint32_t touch_generate_pin_functions(uint8_t *c){
 uint8_t *i=ptr(c,8);uint32_t *f=(uint32_t *)(ptr(c,36)+112);
 for(unsigned j=0;j<14;j++)i[99+j]=255;
 i[104]=0;unsigned count=1;
 if(i[116]==1){i[99]=1;count=2;}else if(i[116]==2){i[100]=1;count=2;}
 i[107]=(uint8_t)count++;i[98]=(uint8_t)count;
 for(unsigned j=0;j<14;j++)if(i[99+j]!=255)f[i[99+j]]=pin_functions[j];
 return 0;
}
uint32_t touch_generate_base(uint8_t *c){
 uint8_t *i=ptr(c,8),*common=ptr(c,0);uint32_t *f=(uint32_t *)ptr(c,36);
 f[0]=0x100011u|(((uint32_t)i[113]<<16)&0x30000u);
 f[1]=0x10000000u|(common[55]&7u)|(((uint32_t)common[56]<<8)&0x100u);
 f[2]=(u16(i,68)?((uint32_t)u16(i,68)<<8)&0xf00u:0x100u)|(u16(i,66)?u16(i,66)&255u:1u)|(((uint32_t)common[54]<<12)&0x1000u);
 f[3]=(u16(i,48)&0xfffu)|(((uint32_t)u16(i,50)<<16)&0xfff0000u);f[4]=0;f[5]=i[83];
 f[6]=i[77]|(((uint32_t)u16(i,64)<<16)&0xf0000u)|(((uint32_t)u16(i,62)<<8)&0x1f00u);f[7]=0x10000u;
 f[8]=(u16(i,60)&0xfffu)|(((uint32_t)i[78]<<16)&0xf0000u);f[9]=0;f[10]=(uint32_t)i[84]<<8;
 f[11]=i[79]|((uint32_t)i[80]<<16);f[12]=0x101u;
 /* Word13 is deliberately retained; stock does not clear the whole frame. */
 f[14]=f[15]=f[16]=0;f[17]=6u|((((uint32_t)i[81]-1u)<<16)&0x3ff0000u);
 for(unsigned j=18;j<=23;j++)f[j]=0;
 f[24]=f[25]=f[26]=0x320023u;f[27]=0;
 touch_generate_modes(c);return touch_generate_pin_functions(c);
}
