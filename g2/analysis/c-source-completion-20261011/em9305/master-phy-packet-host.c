#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t storage[512],*record;static unsigned fail,allocbytes,headerlen,enqueue,posted,cb;
static uintptr_t expectheader,expectpayload;
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){allocbytes=n;return fail?0:(uintptr_t)storage;}
uintptr_t opencfw_em9305_ll_segment_header_323d70(uintptr_t p,uintptr_t f){uint8_t*x=(void*)f;if(p!=(uintptr_t)storage||x[0]!=3||x[1]||x[2]||x[3]||x[4]||x[5]!=(uint8_t)(allocbytes-6)||x[6]||x[7])abort();return headerlen;}
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t q,uint32_t h,uintptr_t e){if(q!=(uintptr_t)(record+360)||h!=255||e!=expectheader)abort();enqueue++;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t h,uint32_t e){if(h!=*(volatile uint8_t*)0x805b18||e!=4||!enqueue)abort();posted++;return 0;}
uint32_t opencfw_em9305_ll_segment_notify_3181b4(uintptr_t p){if(p!=(uintptr_t)record||!posted)abort();return 123;}
uint32_t callback(uintptr_t a,uintptr_t h,uintptr_t p,uintptr_t end){if(a!=(uintptr_t)(record+84)||h!=expectheader||p!=expectpayload||end!=p+*(uint8_t*)(h+1)||record[378]!=42)abort();*(volatile uint8_t*)0x805b18=7;cb++;return 55;}
/* Native32d2f0..32d328 full packet allocation and segment header construction. */
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes)
{
 uintptr_t packet=opencfw_em9305_wsf_event_allocate(bytes+6u);
 if(packet==0u)return 0u;
 uint8_t fields[8]={3u,0u,0u,0u,0u,(uint8_t)bytes,0u,0u};
 uintptr_t length=opencfw_em9305_ll_segment_header_323d70(packet,(uintptr_t)fields);
 return (uint32_t)(packet+length);
}
/* Native32d32c..32d37c complete packet enqueue; callback ABI R0..R3. */
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t record,uintptr_t payload)
{
 uint32_t previous=*(volatile uint8_t *)(record+378u);
 *(volatile uint8_t *)(record+378u)=(uint8_t)(previous+1u);
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8051e0u;
 uint32_t opcode=*(volatile uint8_t *)payload;
 uintptr_t header=payload-(opcode==27u?3u:2u);
 if(callback!=0u){
  uint32_t length=*(volatile uint8_t *)(header+1u);
  (void)((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uintptr_t))callback)(record+84u,header,payload,payload+length);
 }
 (void)opencfw_em9305_ll_event_enqueue(record+360u,255u,header);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 (void)opencfw_em9305_wsf_event_post(handler,4u);
 return opencfw_em9305_ll_segment_notify_3181b4(record);
}

int main(void){
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned count=0;
 for(unsigned n=0;n<65536;n++)for(fail=0;fail<2;fail++)for(headerlen=2;headerlen<=3;headerlen++){
 uintptr_t result=opencfw_em9305_phy_packet_alloc_32d2f0(n);
 if(allocbytes!=n+6||result!=(fail?0:(uint32_t)(uintptr_t)(storage+headerlen)))abort();
 count++;
 }
 uint8_t r[800];record=r;expectpayload=(uintptr_t)(storage+16);
 for(unsigned opcode=0;opcode<256;opcode++)for(unsigned length=0;length<256;length++)for(unsigned present=0;present<2;present++){
 memset(storage,0xa5,sizeof storage);memset(r,0,sizeof r);r[378]=41;storage[16]=(uint8_t)opcode;expectheader=expectpayload-(opcode==27?3:2);*(uint8_t*)(expectheader+1)=(uint8_t)length;
 *(volatile uint32_t*)0x8051e0=present?(uint32_t)(uintptr_t)callback:0;*(volatile uint8_t*)0x805b18=3;enqueue=posted=cb=0;
 if(opencfw_em9305_phy_packet_send_32d32c((uintptr_t)r,expectpayload)!=123||r[378]!=42||enqueue!=1||posted!=1||cb!=present)abort();
 count++;
 }
 printf("PASS %u allocation/enqueue cases\n",count);return 0;
}
