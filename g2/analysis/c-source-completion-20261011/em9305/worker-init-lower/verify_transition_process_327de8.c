#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_process_327de8(uintptr_t);
static uint32_t stage,latest_result,insert_calls,task_calls,post_calls;
static uint32_t random_calls,retry_insert;
static uint32_t peer_found,identity_found;
static uint32_t latest_time_override,expected_elapsed_a;
uint32_t opencfw_em9305_radio_peer_pair_303a40(
    uint32_t a,uint32_t b,uint32_t c,uintptr_t out)
{assert(peer_found&&a==0x11u&&b==0x22334455u&&c==0x66778899u);
 *(uint32_t *)out=0x12345678u;*(uint32_t *)(out+4u)=0x9abcdef0u;
 return 1u;}
uint32_t opencfw_em9305_radio_identity_pair_303a60(
    uint32_t a,uint32_t b,uint32_t c,uintptr_t out)
{if(!identity_found)return 0u;
 assert(a==0x22u&&b==0x33445566u&&c==0x778899aau);
 *(uint32_t *)out=0x11112222u;*(uint32_t *)(out+4u)=0x33334444u;
 return 1u;}
uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t out,uint32_t low,uint32_t high)
{uint16_t upper=(uint16_t)high;
 memcpy((void *)out,&low,sizeof low);
 memcpy((void *)(out+4u),&upper,sizeof upper);
 return out;}
void *opencfw_em9305_memcpy(void *out,const void *in,uint32_t count)
{return memcpy(out,in,count);}
uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object,uint32_t zero)
{assert(object==0x803000u&&zero==0u);stage=1u;return 0u;}
uint32_t opencfw_em9305_init_transition_random_317afc(void)
{++random_calls;return 3u;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,uintptr_t tie)
{assert(stage==1u&&object==0x803000u&&tie==0u);++insert_calls;
 return retry_insert&&insert_calls==1u?0u:1u;}
uint32_t opencfw_em9305_init_schedule_adjust_312f88(
    uintptr_t object,uint32_t minimum,uint32_t maximum)
{(void)object;(void)minimum;(void)maximum;assert(0);return 0u;}
uint32_t opencfw_em9305_init_schedule_latest_3130d4(
    uintptr_t object,uint32_t minimum,uint32_t maximum)
{assert(stage==1u&&object==0x803000u&&minimum==2u&&maximum==3u);
 if(latest_time_override)*(uint32_t *)(object+8u)=latest_time_override;
 return latest_result;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t a,uint32_t b)
{if(expected_elapsed_a){assert(a==expected_elapsed_a);expected_elapsed_a=0u;}
 uint32_t diff=a-b;return (diff&0x80000000u)?0u:diff;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes)
{assert(bytes==4u);++task_calls;return 0x806000u;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message)
{assert(handler==0x12u&&message==0x806000u);
 assert(*(uint16_t *)(message+2u)==1028u);++task_calls;return 0x777u;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t bits)
{assert(handler==0x12u&&bits==1u<<14u);++post_calls;return 0x888u;}
static void reset(void)
{memset((void *)(uintptr_t)0x800000u,0,0x100000u);
 stage=latest_result=insert_calls=task_calls=post_calls=0u;
 random_calls=retry_insert=peer_found=identity_found=0u;
 latest_time_override=expected_elapsed_a=0u;
 *(uint32_t *)(uintptr_t)0x80302cu=0x804000u;
 *(uint8_t *)(uintptr_t)0x805b18u=0x12u;}
int main(void)
{void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
     PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
 assert(p!=(void *)-1);
 reset();*(uint8_t *)(uintptr_t)0x8052fcu=1u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0x777u);
 assert(task_calls==2u&&stage==0u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=0u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(stage==1u&&task_calls==0u&&insert_calls==1u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=2u;
 *(uint32_t *)(uintptr_t)0x805b88u=4u;
 *(uint32_t *)(uintptr_t)0x805b8cu=4u;
 *(uint32_t *)(uintptr_t)0x803008u=100u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(insert_calls==1u&&*(uint32_t *)(uintptr_t)0x803008u==104u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=2u;
 *(uint8_t *)(uintptr_t)0x805a8bu=2u;
 *(uint32_t *)(uintptr_t)0x805b88u=4u;
 *(uint32_t *)(uintptr_t)0x805b8cu=4u;
 retry_insert=1u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(insert_calls==2u&&random_calls==2u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=2u;
 *(uint32_t *)(uintptr_t)0x805b88u=4u;
 *(uint32_t *)(uintptr_t)0x805b8cu=4u;
 *(uint8_t *)(uintptr_t)0x805befu=1u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0x888u);
 assert(post_calls==1u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=1u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0x777u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=1u;
 *(uint32_t *)(uintptr_t)0x805b84u=10u;
 *(uint32_t *)(uintptr_t)0x805b88u=2u;
 *(uint32_t *)(uintptr_t)0x805b8cu=3u;
 *(uint32_t *)(uintptr_t)0x803008u=100u;
 latest_result=1u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==UINT32_MAX);
 assert(task_calls==0u&&*(uint32_t *)(uintptr_t)0x805b84u==10u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=1u;
 *(uint32_t *)(uintptr_t)0x805b84u=10u;
 *(uint32_t *)(uintptr_t)0x805b88u=2u;
 *(uint32_t *)(uintptr_t)0x805b8cu=3u;
 *(uint32_t *)(uintptr_t)0x803008u=100u;
 latest_result=0u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0x777u);
 assert(task_calls==2u&&*(uint32_t *)(uintptr_t)0x803008u==109u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=1u;
 *(uint32_t *)(uintptr_t)0x805b84u=10u;
 *(uint32_t *)(uintptr_t)0x805b88u=2u;
 *(uint32_t *)(uintptr_t)0x805b8cu=3u;
 *(uint32_t *)(uintptr_t)0x803008u=100u;
 latest_result=1u;latest_time_override=120u;expected_elapsed_a=120u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==UINT32_MAX);
 assert(*(uint32_t *)(uintptr_t)0x803008u==120u&&expected_elapsed_a==0u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=1u;
 *(uint32_t *)(uintptr_t)0x805b84u=10u;
 *(uint32_t *)(uintptr_t)0x805b88u=2u;
 *(uint32_t *)(uintptr_t)0x805b8cu=3u;
 *(uint32_t *)(uintptr_t)0x803008u=100u;
 latest_result=0u;latest_time_override=120u;expected_elapsed_a=123u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0x777u);
 assert(*(uint32_t *)(uintptr_t)0x803008u==123u&&expected_elapsed_a==0u);
 reset();*(uint8_t *)(uintptr_t)0x805a7fu=1u;
 *(uint8_t *)(uintptr_t)0x805be2u=1u;
 *(uint32_t *)(uintptr_t)0x805a8cu=0x11223344u;
 *(uint32_t *)(uintptr_t)0x805a90u=0x55667788u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(*(uint8_t *)(uintptr_t)0x805a7fu==0u);
 assert(*(uint16_t *)(uintptr_t)0x8053d2u==0x3344u);
 assert(*(uint16_t *)(uintptr_t)0x8053d4u==0x1122u);
 assert(*(uint16_t *)(uintptr_t)0x8053d6u==0x7788u);
 assert(*(uint32_t *)(uintptr_t)0x804054u==0x11223344u);
 assert(*(uint32_t *)(uintptr_t)0x804058u==0x55667788u);
 reset();peer_found=1u;
 *(uint8_t *)(uintptr_t)0x805be2u=2u;
 *(uint8_t *)(uintptr_t)0x805b92u=0x11u;
 *(uint32_t *)(uintptr_t)0x805b94u=0x22334455u;
 *(uint32_t *)(uintptr_t)0x805b98u=0x66778899u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(*(uint32_t *)(uintptr_t)0x804054u==0x12345678u);
 assert(*(uint32_t *)(uintptr_t)0x804058u==0x9abcdef0u);
 reset();*(uint8_t *)(uintptr_t)0x805b90u=2u;
 *(uint8_t *)(uintptr_t)0x805bc0u=1u;
 *(uint8_t *)(uintptr_t)0x805be1u=1u;
 *(uint8_t *)(uintptr_t)0x805bbfu=3u;
 *(uint8_t *)(uintptr_t)0x805be0u=3u;
 *(uint8_t *)(uintptr_t)0x805ba0u=0xa1u;
 *(uint8_t *)(uintptr_t)0x805ba1u=0xa2u;
 *(uint8_t *)(uintptr_t)0x805ba2u=0xa3u;
 *(uint8_t *)(uintptr_t)0x805bc1u=0xb1u;
 *(uint8_t *)(uintptr_t)0x805bc2u=0xb2u;
 *(uint8_t *)(uintptr_t)0x805bc3u=0xb3u;
 assert(opencfw_em9305_init_transition_process_327de8(0x803000u)==0u);
 assert(*(uint8_t *)(uintptr_t)0x8052dcu==0xa1u);
 assert(*(uint8_t *)(uintptr_t)0x8052ddu==0xa2u);
 assert(*(uint8_t *)(uintptr_t)0x8052deu==0xa3u);
 assert(*(uint8_t *)(uintptr_t)0x8053d1u==9u);
 assert(*(uint8_t *)(uintptr_t)0x8053d8u==0xb1u);
 assert(*(uint8_t *)(uintptr_t)0x80407cu==11u);
 assert(*(uint8_t *)(uintptr_t)0x80407du==11u);
 return 0;}
