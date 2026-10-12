#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation;static unsigned copies;
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==246);return allocation?0x830000:0;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){copies++;return memcpy(d,s,n);}
/* Authenticated fragmented-report helpers32e48c/32e4a8/330f48. Fixed246
 * allocator request, header old-address store then two-byte advance. */
uintptr_t opencfw_em9305_ll_fragment_allocate_32e48c(uint32_t code,uint32_t length)
{
 uintptr_t block=opencfw_em9305_wsf_event_allocate(246u);
 if(block==0u)return 0u;
 *(volatile uint8_t *)(block+1u)=(uint8_t)length;
 *(volatile uint8_t *)block=(uint8_t)code;
 return block+2u;
}
uintptr_t opencfw_em9305_ll_fragment_allocate_32e4a8(uint32_t code,uint32_t length)
{
 uintptr_t block=opencfw_em9305_wsf_event_allocate(246u);
 if(block==0u)return 0u;
 *(volatile uint8_t *)(block+1u)=(uint8_t)length;
 *(volatile uint8_t *)block=(uint8_t)code;
 return block+2u;
}
uintptr_t opencfw_em9305_ll_fragment_format_330f48(uintptr_t output,uintptr_t input,uintptr_t data,uint32_t bytes)
{
 uintptr_t original=*(volatile uint32_t *)(input+16u);
 uintptr_t end=data+bytes;
 uint32_t expected=*(volatile uint8_t *)(input+13u);
 uint32_t status=1u;
 if((uint16_t)(end-original)==expected){
  uint32_t mode=*(volatile uint8_t *)(input+12u);
  status=mode==255u?0xffffffffu:mode==2u?2u:0u;
 }
 *(volatile uint8_t *)output=40u;
 *(volatile uint8_t *)(output+1u)=*(volatile uint8_t *)(input+4u);
 *(volatile uint8_t *)(output+2u)=*(volatile uint8_t *)(input+5u);
 uint32_t captured=*(volatile uint8_t *)(input+6u);
 *(volatile uint8_t *)(output+4u)=1u;
 *(volatile uint8_t *)(output+3u)=(uint8_t)captured;
 *(volatile uint8_t *)(output+5u)=*(volatile uint8_t *)(input+8u);
 *(volatile uint8_t *)(output+6u)=*(volatile uint8_t *)(input+9u);
 *(volatile uint8_t *)(output+7u)=*(volatile uint8_t *)(input+10u);
 captured=*(volatile uint8_t *)(input+11u);
 *(volatile uint8_t *)(output+10u)=(uint8_t)bytes;
 *(volatile uint8_t *)(output+9u)=(uint8_t)status;
 *(volatile uint8_t *)(output+8u)=(uint8_t)captured;
 if(bytes==0u)return output;
 return (uintptr_t)opencfw_em9305_memcpy((void *)(output+11u),(const void *)data,bytes);
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned alloc=0;alloc<2;alloc++)for(unsigned length=0;length<512;length++){allocation=alloc;assert(opencfw_em9305_ll_fragment_allocate_32e48c(0x13e,length)==(alloc?0x830002:0));assert(opencfw_em9305_ll_fragment_allocate_32e4a8(0x23e,length)==(alloc?0x830002:0));if(alloc)assert(*(uint8_t *)0x830000==0x3e&&*(uint8_t *)0x830001==(uint8_t)length);cases++;}
uintptr_t input=0x810000,output=0x820000,data=0x840000;for(unsigned i=0;i<32;i++)*(uint8_t *)(input+i)=i;for(unsigned i=0;i<256;i++)*(uint8_t *)(data+i)=i;
for(unsigned mode=0;mode<256;mode++)for(unsigned bytes=0;bytes<256;bytes++)for(unsigned complete=0;complete<2;complete++){*(uint32_t *)(input+16)=data;*(uint8_t *)(input+13)=complete?bytes:(uint8_t)(bytes+1);*(uint8_t *)(input+12)=mode;copies=0;assert(opencfw_em9305_ll_fragment_format_330f48(output,input,data,bytes)==(bytes?output+11:output));assert(copies==(bytes!=0));uint8_t *out=(uint8_t *)output;assert(out[0]==40&&out[1]==4&&out[2]==5&&out[3]==6&&out[4]==1&&out[5]==8&&out[6]==9&&out[7]==10&&out[8]==11&&out[9]==(complete?(mode==255?255:mode==2?2:0):1)&&out[10]==bytes&&!memcmp(out+11,(void *)data,bytes));cases++;}
printf("PASS %u\n",cases);}
