#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocfail,posts,adjustcalls,failures,inserts,writes;static uint32_t last1,last2;
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=4)abort();return allocfail?0:0x807000;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){if(h!=9||m!=0x807000||*(uint8_t*)(m+3)!=3||*(uint16_t*)m!=0xa5a5)abort();posts++;return 91;}
static uint32_t opencfw_em9305_radio_address_write_3045e8(uintptr_t p,uint32_t l,uint32_t h){if(p!=0x804002||l!=11||h!=12)abort();writes++;*(uint32_t*)0x805a8c=21;*(uint32_t*)0x805a90=22;return 0;}
static uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b){return b-a;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t o){inserts++;*(uint32_t*)(o+8)=77;return 8;}
uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t o,uint32_t a,uint32_t b){if(o!=0x806000)abort();last1=a;last2=b;return ++adjustcalls>failures;}
#include "init-schedule-finish-prepared.c"
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(unsigned pending=0;pending<3;pending++)for(allocfail=0;allocfail<2;allocfail++)for(unsigned flags=0;flags<4;flags++)for(unsigned unequal=0;unequal<2;unequal++)for(failures=0;failures<3;failures++){
memset((void*)0x800000,0,0x10000);memset((void*)0x807000,0xa5,4);posts=adjustcalls=inserts=writes=0;
*(uint32_t*)0x806024=0x804000;*(uint8_t*)(0x804000+148)=pending==1;*(uint8_t*)(0x804000+149)=pending==2;*(uint8_t*)0x805b18=9;
*(uint8_t*)0x805a80=1;*(uint8_t*)(0x804000+65)=flags;*(uint32_t*)0x805a8c=11;*(uint32_t*)0x805a90=12;
*(uint16_t*)(0x804000+60)=1;*(uint16_t*)(0x804000+62)=unequal?2:1;*(uint32_t*)(0x804000+56)=100;*(uint8_t*)(0x804000+201)=37;*(uint8_t*)(0x804000+351)=7;
/* Force normal unequal retry path through duration >= period. */
*(uint32_t*)0x80600c=2000;
uint32_t result=opencfw_em9305_init_schedule_finish_31ec40(0x806000);
if(pending){if(result!=(allocfail?0:91)||posts!=!allocfail||adjustcalls||inserts||writes)abort();if(!allocfail&&*(uint8_t*)0x807002!=3)abort();}
else {if(writes!=((flags&1)&&!(flags&2))||posts)abort();if(flags&1){if(*(uint8_t*)0x805a80||*(uint32_t*)(0x804000+284)!=(writes?21:11)||*(uint32_t*)(0x804000+288)!=(writes?22:12))abort();}if(unequal){if(adjustcalls!=failures+1||last1!=625||last2!=1875||result!=625||*(uint32_t*)(0x804000+364)!=625)abort();}else if(result!=77||inserts!=1||adjustcalls)abort();if(*(uint8_t*)(0x804000+201)!=38)abort();}
cases++;
}
memset((void*)0x800000,0,0x10000);adjustcalls=0;failures=0;*(uint32_t*)0x806024=0x804000;*(uint16_t*)(0x804000+60)=1;*(uint16_t*)(0x804000+62)=2;*(uint32_t*)(0x804000+56)=123;*(uint32_t*)(0x804000+364)=17;
if(opencfw_em9305_init_schedule_finish_31ec40(0x806000)!=0||adjustcalls!=1||last1!=17||last2!=1250||*(uint32_t*)(0x804000+364)!=0)abort();
cases++;
for(unsigned mask=1;mask<8;mask++)for(unsigned ch=37;ch<40;ch++){unsigned expected=ch;do{expected++;if(expected>39)expected=37;}while(!(mask&(1u<<(expected-37))));if(opencfw_em9305_init_channel_next_325720(ch,mask)!=expected)abort();cases++;}
printf("PASS %u isolated finalizer/channel cases\n",cases);return 0;}
