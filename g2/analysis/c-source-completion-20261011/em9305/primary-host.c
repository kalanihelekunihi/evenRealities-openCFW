#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned accept,which,calls,response,rs,rl;static uintptr_t arg0,arg1;static uint8_t snapshot[20];
static uint32_t opencfw_em9305_command_30cba0(uintptr_t p){which=10;memcpy(snapshot,(void*)p,20);return 10;}
static uint32_t opencfw_em9305_command_30e120(uintptr_t p){which=11;memcpy(snapshot,(void*)p,20);return 11;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
uint32_t opencfw_em9305_primary_vendor_32eb34(uintptr_t a,uintptr_t b){(void)a;(void)b;calls++;return accept==1;}
uint32_t opencfw_em9305_primary_private_304afc(uintptr_t a,uintptr_t b){(void)a;(void)b;calls++;return accept==2;}
uint32_t opencfw_em9305_primary_response_32e918(uintptr_t a,uint32_t b,uint32_t c){(void)a;response++;rs=b;rl=c;return 0;}
uint32_t opencfw_em9305_primary_reset_mode_310718(uint32_t a){if(a!=2)abort();return 99;}
uint32_t opencfw_em9305_ll_special_mode_initialize(uint32_t a){if(a!=99)abort();which=1;return 0;}
uint32_t opencfw_em9305_command_primary_30de38(uintptr_t a){which=2;arg0=a;return 2;}
uint32_t opencfw_em9305_command_primary_30b190(uint32_t a){which=3;arg0=a;return 3;}
uint32_t opencfw_em9305_command_primary_30af98(uint32_t a,uintptr_t b){which=4;arg0=a;arg1=b;return 4;}
uint32_t opencfw_em9305_command_primary_30cac4(uint32_t a,uintptr_t b){which=5;arg0=a;arg1=b;return 5;}
uint32_t opencfw_em9305_primary_masks_332b60(uintptr_t a,uintptr_t b){which=6;arg0=a;arg1=b;return 6;}
uint32_t opencfw_em9305_command_primary_30e3ec(int32_t a,int32_t b){which=7;arg0=(uint32_t)a;arg1=(uint32_t)b;return 7;}
uint32_t opencfw_em9305_command_primary_30d528(uint32_t a){which=8;arg0=a;return 8;}
uint32_t opencfw_em9305_command_primary_30d8a0(uint32_t a,uint32_t b){which=9;arg0=a;arg1=b;return 9;}
/* Native32e5d4..32e914: primary HCI command dispatch. Stack projections
 * intentionally retain native unwritten padding; helper/data contracts remain explicit. */
extern uint32_t opencfw_em9305_primary_vendor_32eb34(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_private_304afc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_response_32e918(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_primary_reset_mode_310718(uint32_t);
extern uint32_t opencfw_em9305_ll_special_mode_initialize(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30de38(uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30b190(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30af98(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30cac4(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_masks_332b60(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30e3ec(int32_t,int32_t);
extern uint32_t opencfw_em9305_command_primary_30d528(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30d8a0(uint32_t,uint32_t);
uint32_t opencfw_em9305_ll_command_primary(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_primary_vendor_32eb34(request,input)!=0u)return 1u;
 if(opencfw_em9305_primary_private_304afc(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request,status=0u,length=9u;
 _Alignas(4) uint8_t scratch[20];
 switch(command){
 case 0x0c03u:{uint32_t value=opencfw_em9305_primary_reset_mode_310718(2u);uintptr_t result=opencfw_em9305_ll_special_mode_initialize(value);(void)result;(void)opencfw_em9305_memset((void *)(uintptr_t)0x8056e8u,0u,24u);return 1u;}
 case 0x0c01u:(void)opencfw_em9305_primary_masks_332b60(0x8056e8u,input);length=1u;break;
 case 0x0c63u:(void)opencfw_em9305_primary_masks_332b60(0x8056f0u,input);length=1u;break;
 case 0x2001u:(void)opencfw_em9305_primary_masks_332b60(0x8056f8u,input);length=1u;break;
 case 0x0c48u:case 0x200fu:length=2u;break;
 case 0x0c49u:*(volatile uint8_t *)(uintptr_t)0x80571au=*(volatile uint8_t *)input;length=1u;break;
 case 0x2002u:length=4u;break;
 case 0x2005u:status=opencfw_em9305_command_primary_30de38(input);length=1u;break;
 case 0x2010u:status=opencfw_em9305_command_primary_30b190(command);length=1u;break;
 case 0x2011u:status=opencfw_em9305_command_primary_30af98(*(volatile uint8_t *)input,input+1u);length=1u;break;
 case 0x2012u:status=opencfw_em9305_command_primary_30cac4(*(volatile uint8_t *)input,input+1u);length=1u;break;
 case 0x201du:{uint32_t id=*(volatile uint8_t *)input;*(volatile uint8_t *)(scratch+8u)=(uint8_t)id;*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+16u)=0u;*(volatile uint8_t *)(scratch+14u)=2u;*(volatile uint16_t *)(scratch+10u)=0u;*(volatile uint8_t *)(scratch+9u)=1u;*(volatile uint32_t *)(scratch+4u)=0x71764129u;*(volatile uint16_t *)(scratch+12u)=256u;status=opencfw_em9305_command_30cba0((uintptr_t)scratch);length=1u;break;}
 case 0x201eu:{uint32_t b2=*(volatile uint8_t *)(input+2u),b0=*(volatile uint8_t *)input,b1=*(volatile uint8_t *)(input+1u);*(volatile uint8_t *)(scratch+4u)=(uint8_t)b2;*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+12u)=0u;*(volatile uint8_t *)(scratch+8u)=2u;*(volatile uint16_t *)(scratch+6u)=0u;*(volatile uint8_t *)(scratch+5u)=1u;*(volatile uint8_t *)(scratch+16u)=127u;*(volatile uint8_t *)(scratch+2u)=(uint8_t)b0;*(volatile uint8_t *)(scratch+3u)=(uint8_t)b1;status=opencfw_em9305_command_30e120((uintptr_t)scratch);length=1u;break;}
 case 0x201fu:case 0x204bu:length=3u;break;
 case 0x204cu:length=5u;break;
 case 0x204du:{uint32_t b1=*(volatile uint8_t *)(input+1u),b3=*(volatile uint8_t *)(input+3u),b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u);status=opencfw_em9305_command_primary_30e3ec((int16_t)(b0+(b1<<8u)),(int16_t)(b2+(b3<<8u)));length=1u;break;}
 case 0x204fu:{uint32_t b[7];b[6]=*(volatile uint8_t *)(input+6u);for(uint32_t i=0u;i<6u;i++)b[i]=*(volatile uint8_t *)(input+i);*(volatile uint8_t *)(scratch+14u)=(uint8_t)b[6];*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+4u)=0x71764129u;*(volatile uint32_t *)(scratch+16u)=(uint32_t)(input+7u);for(uint32_t i=0u;i<6u;i++)*(volatile uint8_t *)(scratch+8u+i)=(uint8_t)b[i];status=opencfw_em9305_command_30cba0((uintptr_t)scratch);length=1u;break;}
 case 0x2050u:{uint32_t b[7];b[1]=*(volatile uint8_t *)(input+1u);b[0]=*(volatile uint8_t *)input;for(uint32_t i=2u;i<7u;i++)b[i]=*(volatile uint8_t *)(input+i);*(volatile uint8_t *)(scratch+3u)=(uint8_t)b[1];*(volatile uint16_t *)scratch=0u;*(volatile uint8_t *)(scratch+16u)=127u;*(volatile uint32_t *)(scratch+12u)=(uint32_t)(input+7u);*(volatile uint8_t *)(scratch+2u)=(uint8_t)b[0];for(uint32_t i=2u;i<7u;i++)*(volatile uint8_t *)(scratch+2u+i)=(uint8_t)b[i];status=opencfw_em9305_command_30e120((uintptr_t)scratch);length=1u;break;}
 case 0x0c82u:{uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input;status=opencfw_em9305_command_primary_30d528((uint16_t)(b0+(b1<<8u)));length=1u;break;}
 case 0x0c84u:{uint32_t value=*(volatile uint8_t *)input;status=value!=0u&&value<17u?17u:0u;length=1u;break;}
 case 0x2074u:{uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input;status=opencfw_em9305_command_primary_30d8a0(b0,b1!=0u);length=1u;break;}
 case 0x205fu:status=12u;length=1u;break;
 case 0x207bu:status=1u;length=1u;break;
 case 0x1002u:length=65u;break;
 case 0x1009u:length=7u;break;
 case 0u:length=1u;break;
 case 0x1001u:case 0x1003u:case 0x2003u:case 0x2018u:case 0x201cu:break;
 default:return 0u;
 }
 (void)opencfw_em9305_primary_response_32e918(request,(uint8_t)status,length);
 return 1u;
}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;uint16_t req;uint8_t input[16]={0x81,0xff,3,0x80,5,6,7};unsigned n=0;for(accept=0;accept<3;accept++)for(unsigned op=0;op<65536;op++){req=op;which=calls=response=0;rs=rl=999;arg0=arg1=0;unsigned expected=0,len=9,status=0,helper=0;switch(op){case 0x0c03:expected=1;helper=1;break;case 0x0c01:case 0x0c63:case 0x2001:expected=1;len=1;helper=6;break;case 0x0c48:case 0x200f:expected=1;len=2;break;case 0x0c49:expected=1;len=1;break;case 0x2002:expected=1;len=4;break;case 0x2005:helper=2;goto child;case 0x2010:helper=3;goto child;case 0x2011:helper=4;goto child;case 0x2012:helper=5;goto child;case 0x201d:case 0x204f:helper=10;goto child;case 0x201e:case 0x2050:helper=11;goto child;case 0x204d:helper=7;goto child;case 0x0c82:helper=8;goto child;case 0x2074:helper=9;child:status=helper;expected=1;len=1;break;case 0x201f:case 0x204b:expected=1;len=3;break;case 0x204c:expected=1;len=5;break;case 0x0c84:expected=1;len=1;status=input[0]>0&&input[0]<17?17:0;break;case 0x205f:expected=1;len=1;status=12;break;case 0x207b:expected=1;len=1;status=1;break;case 0x1002:expected=1;len=65;break;case 0x1009:expected=1;len=7;break;case 0:expected=1;len=1;break;case 0x1001:case 0x1003:case 0x2003:case 0x2018:case 0x201c:expected=1;break;}
unsigned got=opencfw_em9305_ll_command_primary((uintptr_t)&req,(uintptr_t)input);if(accept){if(got!=1||which||response||calls!=(accept==1?1:2))abort();}else{if(got!=expected||which!=helper||response!=(expected&&op!=0xc03))abort();if(response&&(rs!=status||rl!=len))abort();if(helper==2&&arg0!=(uintptr_t)input)abort();if(helper==3&&arg0!=op)abort();if((helper==4||helper==5)&&(arg0!=input[0]||arg1!=(uintptr_t)(input+1)))abort();if(helper==6&&(arg1!=(uintptr_t)input||arg0!=(op==0xc01?0x8056e8:op==0xc63?0x8056f0:0x8056f8)))abort();if(helper==7&&(arg0!=(uint32_t)(int32_t)(int16_t)0xff81||arg1!=(uint32_t)(int32_t)(int16_t)0x8003))abort();if(helper==8&&arg0!=0xff81)abort();if(helper==9&&(arg0!=0x81||arg1!=1))abort();}n++;}
accept=0;req=0xc84;for(unsigned i=0;i<256;i++){input[0]=i;response=0;opencfw_em9305_ll_command_primary((uintptr_t)&req,(uintptr_t)input);if(response!=1||rs!=(i&&i<17?17:0)||rl!=1)abort();n++;}unsigned ops[]={0x201d,0x201e,0x204f,0x2050};for(unsigned k=0;k<4;k++){req=ops[k];for(unsigned i=0;i<16;i++)input[i]=i+21;opencfw_em9305_ll_command_primary((uintptr_t)&req,(uintptr_t)input);uint16_t z;memcpy(&z,snapshot,2);if(z)abort();uint32_t v;if(k==0||k==2){memcpy(&v,snapshot+4,4);if(v!=0x71764129)abort();if(k==0){memcpy(&v,snapshot+16,4);if(v||snapshot[8]!=21||snapshot[9]!=1||snapshot[10]||snapshot[11]||snapshot[12]||snapshot[13]!=1||snapshot[14]!=2)abort();}else{memcpy(&v,snapshot+16,4);if(v!=(uint32_t)(uintptr_t)(input+7))abort();for(unsigned i=0;i<7;i++)if(snapshot[8+i]!=input[i])abort();}}else{if(snapshot[16]!=127)abort();if(k==1){memcpy(&v,snapshot+12,4);if(v||snapshot[2]!=21||snapshot[3]!=22||snapshot[4]!=23||snapshot[5]!=1||snapshot[6]||snapshot[7]||snapshot[8]!=2)abort();}else{memcpy(&v,snapshot+12,4);if(v!=(uint32_t)(uintptr_t)(input+7))abort();for(unsigned i=0;i<7;i++)if(snapshot[2+i]!=input[i])abort();}}n++;}printf("PASS %u routing/argument fixtures\n",n);}
