#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned fail,order,powercalls,notify_seen;static int32_t requested;
static uint32_t opencfw_em9305_ll_connection_gate_30e524(void){uint32_t busy=*(volatile uint8_t*)0x805a9f;if(!busy)*(volatile uint8_t*)0x805a9e=1;return !busy;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){if(order!=0)fail++;order=1;return 19;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){if(order!=2)fail++;order=3;return 23;}
static void *opencfw_em9305_memcpy(void*d,const void*s,uint32_t n){if(order==1)order=2;return memcpy(d,s,n);}
extern uint32_t opencfw_em9305_command_advertising_data_notify_306a7c(uint32_t);
extern uint32_t opencfw_em9305_command_radio_power_310230(int32_t,uint32_t);
/* Native30cee4..30ceee: caller input R0 survives the byte store. */
uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t value)
{*(volatile uint8_t *)(uintptr_t)0x805a9cu=(uint8_t)value;return (uint32_t)value;}
/* Native303258..303264: live 32-byte product version, same copy provider. */
void opencfw_em9305_command_product_version_303258(uintptr_t output)
{(void)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8013d0u,32u);}
/* Native30cdd8..30ce18: captured length survives gate and critical calls. */
uint32_t opencfw_em9305_command_advertising_data_30cdd8(uint32_t length,uintptr_t input)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 if(length>=32u)return 18u;
 (void)opencfw_em9305_wsf_critical_enter();
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805ba0u,(const void *)input,length);
 *(volatile uint8_t *)(uintptr_t)0x805bc0u=1u;
 *(volatile uint8_t *)(uintptr_t)0x805bbfu=(uint8_t)length;
 (void)opencfw_em9305_wsf_critical_exit();
 (void)opencfw_em9305_command_advertising_data_notify_306a7c(1u);
 return 0u;
}
/* Native30df98..30dfd8: distinct adjacent scan-response data region. */
uint32_t opencfw_em9305_command_scan_response_30df98(uint32_t length,uintptr_t input)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 if(length>=32u)return 18u;
 (void)opencfw_em9305_wsf_critical_enter();
 (void)opencfw_em9305_memcpy((void *)(uintptr_t)0x805bc1u,(const void *)input,length);
 *(volatile uint8_t *)(uintptr_t)0x805be1u=1u;
 *(volatile uint8_t *)(uintptr_t)0x805be0u=(uint8_t)length;
 (void)opencfw_em9305_wsf_critical_exit();
 (void)opencfw_em9305_command_advertising_data_notify_306a7c(2u);
 return 0u;
}
/* Native30bb50..30bb74: gate failure leaves output untouched. */
uint32_t opencfw_em9305_command_advertising_power_30bb50(uintptr_t output)
{
 if(opencfw_em9305_ll_connection_gate_30e524()==0u)return 12u;
 int32_t requested=(int8_t)*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t actual=opencfw_em9305_command_radio_power_310230(requested,0u);
 *(volatile uint8_t *)output=(uint8_t)actual;
 return 0u;
}

uint32_t opencfw_em9305_command_advertising_data_notify_306a7c(uint32_t type){if(order!=3)fail++;order=4;notify_seen=type;return 91;}
uint32_t opencfw_em9305_command_radio_power_310230(int32_t a,uint32_t b){if(a!=requested||b)fail++;powercalls++;return (uint32_t)(a-7);}
int main(void){if(mmap((void*)0x800000,131072,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)return 2;uintptr_t input=0x810000,out=0x811000;unsigned cases=0;
 for(unsigned type=0;type<2;type++)for(unsigned busy=0;busy<256;busy++)for(unsigned len=0;len<256;len++){
  memset((void*)0x805ba0,0xa5,66);for(unsigned j=0;j<256;j++)*(uint8_t*)(input+j)=(uint8_t)(len+37*j);*(uint8_t*)0x805a9f=busy;*(uint8_t*)0x805a9e=0;order=0;notify_seen=0;
  uint8_t expected[66];memset(expected,0xa5,66);uint32_t want=busy?12:len>=32?18:0;
  if(!want){unsigned base=type?33:0;memcpy(expected+base,(void*)input,len);expected[base+32]=1;expected[base+31]=len;}
  uint32_t result=type?opencfw_em9305_command_scan_response_30df98(len,input):opencfw_em9305_command_advertising_data_30cdd8(len,input);
  if(result!=want||memcmp(expected,(void*)0x805ba0,66)||order!=(!want?4:0)||notify_seen!=(!want?type+1:0)||*(uint8_t*)0x805a9e!=!busy)fail++;cases++;
 }
 for(int32_t v=-32768;v<32768;v++){if(opencfw_em9305_command_vendor_byte_30cee4(v)!=(uint32_t)v||*(uint8_t*)0x805a9c!=(uint8_t)v)fail++;cases++;}
 for(unsigned busy=0;busy<256;busy++)for(unsigned v=0;v<256;v++){
  *(uint8_t*)0x805a9f=busy;*(uint8_t*)0x805a9e=0;*(uint8_t*)0x805a9c=v;*(uint8_t*)out=0xa5;powercalls=0;requested=(int8_t)v;
  uint32_t result=opencfw_em9305_command_advertising_power_30bb50(out);
  if(result!=(busy?12:0)||powercalls!=!busy||*(uint8_t*)out!=(busy?0xa5:(uint8_t)(requested-7))||*(uint8_t*)0x805a9e!=!busy)fail++;cases++;
 }
 for(unsigned seed=0;seed<256;seed++){for(unsigned j=0;j<32;j++)*(uint8_t*)((uintptr_t)0x8013d0+j)=seed+j;memset((void*)out,0xa5,40);order=0;opencfw_em9305_command_product_version_303258(out);if(memcmp((void*)out,(void*)0x8013d0,32))fail++;for(unsigned j=32;j<40;j++)if(*(uint8_t*)(out+j)!=0xa5)fail++;cases++;}
 printf("cases=%u failures=%u\n",cases,fail);return fail?1:0;
}
