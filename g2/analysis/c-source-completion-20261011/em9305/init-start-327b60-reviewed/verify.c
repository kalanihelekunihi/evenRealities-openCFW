#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

uint32_t opencfw_em9305_init_transition_start_327b60(void);
static uint32_t mode,stage,mutate_mode;
void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t n)
{assert(stage==0u&&value==0u&&n==204u&&(uintptr_t)dst==0x805300u);
 stage=1u;return memset(dst,0,n);}
uint32_t opencfw_em9305_init_transition_random_30c478(void)
{assert(stage==1u);stage=2u;return 5u;}
uint32_t opencfw_em9305_init_transition_stage_318290(
    uintptr_t packet,uintptr_t frame,uint32_t r2,uint32_t r3,uint32_t r4,
    uint32_t r5,uintptr_t output)
{assert(stage==1u||stage==2u);assert(packet==0x805330u);
 assert(r2==0x22u&&r3==0x33u&&r4==0x44556677u&&r5==0x8899aabbu);
 assert(frame!=0u);*(uint32_t *)output=0x12121212u;
 *(uint32_t *)(output+4u)=0x34343434u;stage=3u;return 0u;}
uint32_t opencfw_em9305_init_transition_stage_318348(
    uintptr_t packet,uint32_t zero,uint32_t r2,uint32_t r3,uint32_t r4,
    uintptr_t output)
{assert(stage==3u&&packet==0x805330u&&zero==0u);
 assert(r2==0x33u&&r3==0x44556677u&&r4==0x8899aabbu);
 *(uint32_t *)output=0u;*(uint32_t *)(output+4u)=0u;
 stage=4u;return 0u;}
uint32_t opencfw_em9305_init_transition_record_323c78(
    uintptr_t dst,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth)
{assert(stage==4u&&dst==0x8052d6u&&first==0x12121212u&&second==0x34343434u);
 assert(third==0x44556677u&&fourth==0x8899aabbu);
 *(uint32_t *)(uintptr_t)0x805380u=0x80u;
 stage=5u;return 0x850000u;}
uint32_t opencfw_em9305_init_transition_record_3239b8(
    uintptr_t dst,uint32_t first,uint32_t second,uintptr_t source)
{assert(stage==4u&&dst==0x8052d6u&&first==0x12121212u&&
        second==0x34343434u&&source==0x805ba0u);
 stage=5u;return 0x850000u;}
uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,uintptr_t frame)
{assert(frame!=0u);
 if(output==0x8052d4u){
  assert(stage==5u);stage=6u;
  if(mutate_mode)*(uint8_t *)(uintptr_t)0x805b90u=6u;
  return 2u;
 }
 assert(output==0x8053d0u&&(mode==0u||mode==2u));
 assert(stage==6u);
 stage=8u;return 2u;}
uint32_t opencfw_em9305_init_transition_segment_3243dc(
    uint32_t doubled,uint32_t first,uint32_t second,uintptr_t row)
{assert(stage==8u&&doubled==4u&&first==0x12121212u&&
        second==0x34343434u&&row==0x805bc1u);
 stage=9u;return 3u;}
uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t active,uint32_t zero)
{assert(active==0x805300u&&zero==0u);
 assert(stage==6u||stage==9u);stage=10u;return 0u;}
uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t active)
{assert(stage==10u&&active==0x805300u);stage=11u;return 0xfeed1234u;}
void opencfw_em9305_init_transition_process_327de8(void){}
void opencfw_em9305_init_transition_callback_32805c(void){}
void opencfw_em9305_init_transition_callback_328018(void){}

static void run(unsigned m,unsigned mutate)
{
    memset((void *)(uintptr_t)0x800000u,0,0x100000u);
    mode=m;mutate_mode=mutate;stage=0u;
    *(uint8_t *)(uintptr_t)0x805b90u=(uint8_t)m;
    *(uint8_t *)(uintptr_t)0x805a95u=0x40u;
    *(uint8_t *)(uintptr_t)0x805a85u=0x40u;
    *(uint8_t *)(uintptr_t)0x805a9cu=0x77u;
    *(uint8_t *)(uintptr_t)0x805b91u=0x22u;
    *(uint8_t *)(uintptr_t)0x805b92u=0x33u;
    *(uint32_t *)(uintptr_t)0x805b94u=0x44556677u;
    *(uint32_t *)(uintptr_t)0x805b98u=0x8899aabbu;
    *(uint8_t *)(uintptr_t)0x805bc0u=0x5au;
    *(uint32_t *)(uintptr_t)0x805380u=0x80u;
    uint32_t sentinel=0xccccccccu; memcpy((void *)(uintptr_t)0x8500aau,&sentinel,4u);
    uint32_t result=opencfw_em9305_init_transition_start_327b60();
    if(m>4u){assert(stage==2u&&result==2u);return;}
    assert(stage==11u&&result==0xfeed1234u);
    assert(*(uint8_t *)(uintptr_t)0x8053acu==2u);
    memcpy(&sentinel,(const void *)(uintptr_t)0x8500aau,4u); assert(sentinel==0xccccccccu);
    if(m==1u||m==4u)assert(*(uint32_t *)(uintptr_t)0x805380u==0x84u);
    assert(*(uint8_t *)(uintptr_t)0x8053aeu==(m==1u?0u:2u));
    assert(*(uint8_t *)(uintptr_t)0x8053afu==0u);
    assert(*(uint8_t *)(uintptr_t)0x805332u==0x77u);
    assert(*(uint32_t *)(uintptr_t)0x805338u==0x00555555u);
    assert(*(uint32_t *)(uintptr_t)0x805334u==0x8e89bed6u);
    assert(*(uint16_t *)(uintptr_t)0x8052fcu==0u);
    if(m!=1u&&m!=4u)assert(*(uint8_t *)(uintptr_t)0x805bc0u==0u);
    if((m==0u||m==2u)&&!mutate) {
        assert(*(uint8_t *)(uintptr_t)0x805be1u==0u);
        assert(*(uint8_t *)(uintptr_t)0x8053adu==5u);
    }
    if(mutate){
        assert(*(uint8_t *)(uintptr_t)0x805b90u==6u);
        assert(*(uint32_t *)(uintptr_t)0x805398u==0u);
    }
}
int main(void)
{
    void *p=mmap((void *)(uintptr_t)0x800000u,0x100000u,
        PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(p!=(void *)-1);
    for(unsigned i=0;i<6u;i++)run(i,0u);
    run(0u,1u);
    return 0;
}
