/* Independent locked-image flash choreography. SROM is an external test
 * boundary; this is not a physical programming implementation or safe patch. */
#include <stdint.h>
#include "cy_syslib.h"
#define SYSARG (*(volatile uint32_t *)0x40100008u)
#define SYSREQ (*(volatile uint32_t *)0x40100004u)
uint32_t touch_flash_status(void) {
 uint32_t s=SYSARG,kind=s&0xf0000000u;
 if(kind==0xa0000000u)return 0;
 if(kind!=0xf0000000u)return 0x00500023u;
 switch(s) {
 case 0xf0000001u:return 0x00520001u;
 case 0xf0000003u:case 0xf0000004u:return 0x00520004u;
 case 0xf0000005u:return 0x00520005u;
 case 0xf0000007u:return 0;
 case 0xf0000008u:return 0x00500008u;
 case 0xf0000009u:return 0x00500009u;
 case 0xf0000011u:case 0xf0000013u:case 0xf0000014u:return 0x00520021u;
 default:return 0x005200ffu;
 }
}
static uint32_t backup(void) {
 uint32_t p[2]={0xe9b6u,0x20000f04u};SYSARG=(uint32_t)p;SYSREQ=0x80000016u;
 uint32_t result=touch_flash_status();*(volatile uint32_t *)0x40030030u=0x80000000u;return result;
}
static uint32_t configure(void) { SYSARG=0xe8b6u;SYSREQ=0x80000015u;return touch_flash_status(); }
static uint32_t restore(void) { uint32_t p[2]={0xeab6u,0x20000f04u};SYSARG=(uint32_t)p;SYSREQ=0x80000017u;return touch_flash_status(); }
uint32_t touch_flash_write_row(uint32_t address,const uint8_t *data) {
 uint32_t row=(address>0xffffu ? address-0x0ffff200u : address)>>7;
 if(!((address<0x10000u || address-0x0ffff200u<0x200u) && !(address&127u)) || !data)return 0x00520021u;
 uint32_t p[34];for(unsigned i=0;i<128;i++)((uint8_t *)(p+2))[i]=data[i];
 p[0]=0xd7b6u|((row>>9)<<24);p[1]=127;SYSARG=(uint32_t)p;SYSREQ=0x80000004u;
 uint32_t status=touch_flash_status();if(status)return status;
 uint32_t mask=Cy_SysLib_EnterCriticalSection();status=backup();
 if(!status) { status=configure();if(!status) {
  SYSARG=(uint32_t)p;
  if(address>0x0fffefffu) { p[0]=0xebb6u;p[1]=row;SYSREQ=0x80000018u; }
  else { p[0]=0xd8b6u|(row<<16);SYSREQ=0x80000005u; }
  uint32_t written=touch_flash_status();status=restore();if(written)status=written;
 } }
 Cy_SysLib_ExitCriticalSection(mask);return status;
}
