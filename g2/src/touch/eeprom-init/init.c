/* Independent reconstruction of stock initialization and application wrapper.
 * No flash writes. Pinned publicSDK family is a comparator, not copied source.
 * Full function domain is bounded by actual installed128-byte provider. */
#include <stdint.h>
#include "init.h"
#include "provider.h"
#include "history.h"
/* Source-defined data matches the twelve reset-copied bytes at0xb58c. */
const touch_eeprom_configuration touch_factory_eeprom_configuration={256,0,2,1,1,0};
static uint32_t w(const uint8_t *c,unsigned o){return *(const uint32_t *)(c+o);}
static uint16_t h(const uint8_t *c,unsigned o){return *(const uint16_t *)(c+o);}
static uint32_t div32(uint32_t n,uint32_t d){uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
uint32_t touch_provider_read_size(uint32_t handle,uint32_t address){(void)handle;(void)address;return 1;}
uint32_t touch_provider_program_size(uint32_t handle,uint32_t address){(void)handle;(void)address;return 128;}
uint32_t touch_provider_erase_size(uint32_t handle,uint32_t address){(void)handle;(void)address;return 128;}
uint32_t touch_provider_erase_value(uint32_t handle,uint32_t address){(void)handle;(void)address;return 0;}
uint32_t touch_provider_in_range(uint32_t handle,uint32_t address,uint32_t size){(void)handle;return address!=0u&&address+size<=0x10000u;}
uint32_t touch_provider_init(uint32_t *p){
 if(!p)return 0x06160003u;
 p[5]=(uint32_t)touch_storage_copy;p[6]=(uint32_t)touch_storage_program;p[7]=(uint32_t)touch_storage_zero;
 p[8]=0;p[9]=0;p[1]=(uint32_t)touch_provider_read_size;p[2]=(uint32_t)touch_provider_program_size;p[3]=(uint32_t)touch_provider_erase_size;p[4]=(uint32_t)touch_provider_erase_value;p[10]=(uint32_t)touch_provider_in_range;p[11]=(uint32_t)touch_storage_no_erase;p[0]=0;return 0;
}
uint32_t touch_init_physical_size(const uint8_t *c,const uint8_t *cfg){uint32_t size=h(c,0)*h(c,2),simple=cfg[4];return size*(simple+(1u-simple)*cfg[5]*(cfg[6]+1u));}
uint32_t touch_init_ranges(const uint8_t *cfg,const uint8_t *c){
 uint32_t base=w(cfg,8);if(!base||!w(cfg,0)||cfg[4]>1||cfg[7]>1||cfg[6]>1||!cfg[5]||cfg[5]>10)return 0x093e0002u;
 uint32_t *p=(uint32_t *)w(c,28);uint32_t (*range)(uint32_t,uint32_t,uint32_t)=(void *)p[10];return range(p[0],base,touch_init_physical_size(c,cfg))?0:0x093e0002u;
}
void touch_init_program_size(uint8_t *c){
 uint32_t *p=(uint32_t *)w(c,28);uint32_t (*get)(uint32_t,uint32_t)=(void *)p[2];uint32_t size=get(p[0],w(c,16));
 if(c[13]){*(uint16_t *)(c+2)=(uint16_t)size;return;}
 uint16_t row=(uint16_t)((uint16_t)size*(div32(w(c,8)-1u,size)+1u));if(row>w(c,4))row=(uint16_t)w(c,4);if(row<128)row=128;*(uint16_t *)(c+2)=(uint16_t)((uint16_t)size*(div32(row-1u,size)+1u));
}
uint32_t touch_eeprom_init_bd(const uint8_t *cfg,uint8_t *c,uint32_t *p){
 if(!c||!cfg||!p)return 0x093e0000u;
 for(uint32_t i=0;i<32;i++)c[i]=0;
 *(uint32_t *)(c+28)=(uint32_t)p;*(uint32_t *)(c+16)=w(cfg,8);c[13]=cfg[4];*(uint32_t *)(c+8)=w(cfg,0);
 uint32_t (*get)(uint32_t,uint32_t)=(void *)p[3];*(uint32_t *)(c+4)=get(p[0],w(cfg,8));touch_init_program_size(c);
 uint16_t bytes=c[13]==1?h(c,2):h(c,2)>>1;*(uint16_t *)(c+20)=bytes;*(uint16_t *)(c+22)=(uint16_t)(bytes-16u);*(uint16_t *)c=(uint16_t)(div32(w(c,8)-1u,bytes)+1u);
 uint32_t status=touch_init_ranges(cfg,c);if(status)return status;if(!cfg[7])return 0x093e0000u;
 c[12]=c[13]?1:cfg[5];c[14]=c[13]?0:cfg[6];c[15]=cfg[7];(void)touch_define_last(c);return 0;
}
uint32_t touch_eeprom_init(const uint8_t *cfg,uint8_t *c){
 uint32_t *p=(uint32_t *)0x20000ed4u;if(touch_provider_init(p))return 0;uint8_t copy[12];
 *(uint32_t *)copy=w(cfg,0);for(uint32_t i=4;i<8;i++)copy[i]=cfg[i];*(uint32_t *)(copy+8)=w(cfg,8);return touch_eeprom_init_bd(copy,c,p);
}
uint32_t touch_application_eeprom_init(void){
 uint8_t *flag=(uint8_t *)0x200008c4u;if(*flag)return 0;
 uint8_t *cfg=(uint8_t *)0x200004c0u;*(uint32_t *)(cfg+8)=0xe400u;uint32_t status=touch_eeprom_init(cfg,(uint8_t *)0x200008c8u);
 if(!status||status==0x093e0004u){*flag=1;return 0;}return 1;
}
