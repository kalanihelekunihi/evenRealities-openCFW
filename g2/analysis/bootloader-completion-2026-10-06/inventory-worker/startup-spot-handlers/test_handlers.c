#include "handlers.c"
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint32_t fail_at;
    uint32_t reads;
    uint32_t commits;
    uint32_t selector[3], offset[3], count[3];
} fixture;
static uint32_t fake_read(void *opaque, uint32_t selector, uint32_t offset,
                          uint32_t count, uint32_t *dst)
{
    fixture *f = opaque; uint32_t n=f->reads++;
    assert(n<3U); f->selector[n]=selector;f->offset[n]=offset;f->count[n]=count;
    if (f->fail_at==n+1U) return 0x100U+n;
    for (uint32_t i=0;i<count;i++) dst[i]=(n+1U)*0x10000U+i+1U;
    if (n==0U && count==16U) {
        dst[10]=0x10000000U|(33U<<21)|0x4567U;
        dst[12]=0x10000000U|(12U<<21)|(5U<<17)|(0x155U<<7)|0x51U;
        dst[13]=0x10000000U|(18U<<21)|(9U<<17)|(0x2aaU<<7)|0x62U;
    }
    return 0U;
}
static void fake_commit(void *opaque) { ((fixture *)opaque)->commits++; }
static void test_gate_and_call_contract(void)
{
    spot_profile_state s={0};fixture f={0};
    s.power_control=1U<<3;s.kernel_control=0;
    assert(spotmgr_init_42abbc_model(&s,fake_read,fake_commit,&f)==7U);
    assert(f.reads==0&&f.commits==0);
    s.kernel_control=1U<<27;
    assert(spotmgr_init_42abbc_model(&s,fake_read,fake_commit,&f)==0U);
    assert(f.reads==3&&f.commits==1);
    assert(f.selector[0]==1&&f.offset[0]==0x25c&&f.count[0]==20);
    assert(f.selector[1]==1&&f.offset[1]==0x270&&f.count[1]==5);
    assert(f.selector[2]==1&&f.offset[2]==0x278&&f.count[2]==1);
    assert(s.word[1]==0x10001U&&s.word[20]==0x10014U);
    assert(s.word[21]==0x20001U&&s.word[25]==0x20005U&&s.word[26]==0x30001U);
    assert(s.word[0]==0x1f01600dU);
}
static void test_read_errors_stop_before_commit(void)
{
    for(uint32_t fail=1;fail<=3;fail++){
        spot_profile_state s={0};fixture f={.fail_at=fail};
        uint32_t result=spotmgr_init_42abbc_model(&s,fake_read,fake_commit,&f);
        assert(result==0xffU+fail);assert(f.reads==fail);assert(f.commits==0);
        f=(fixture){.fail_at=fail};s=(spot_profile_state){0};
        result=hw_state_compose_42bdf0_model(&s,fake_read,fake_commit,&f);
        assert(result==0xffU+fail);assert(f.reads==fail);assert(f.commits==0);
    }
}
static uint32_t bitfield(uint32_t w,unsigned shift,unsigned width)
{return (w>>shift)&((1U<<width)-1U);}
static void test_hw_state_composition(void)
{
    spot_profile_state s={0};fixture f={0};
    s.power_control=1U<<3;s.kernel_control=1U<<27;
    for(unsigned i=0;i<27;i++)s.word[i]=0xa5a50000U+i;
    s.word[13]=0x10000000U|(12U<<21)|(5U<<17)|(0x155U<<7)|0x51U;
    s.word[14]=0x10000000U|(18U<<21)|(9U<<17)|(0x2aaU<<7)|0x62U;
    s.word[11]=0x10000000U|(33U<<21)|0x4567U;
    assert(hw_state_compose_42bdf0_model(&s,fake_read,fake_commit,&f)==0U);
    assert(f.reads==3&&f.commits==1);
    assert(f.offset[0]==0x25c&&f.count[0]==16&&f.offset[1]==0x270&&f.count[1]==4&&f.offset[2]==0x278&&f.count[2]==1);
    assert((s.word[17]&0x7fU)==(s.word[13]&0x7fU));
    assert((s.word[20]&0x7fU)==(s.word[16]&0x7fU));
    assert(bitfield(s.word[9],21,7)==15U);
    assert(bitfield(s.word[10],21,7)==33U);
    assert(bitfield(s.word[26],20,6)==31U);
    assert(s.word[0]==0x1f01600dU);
}
static void test_flag_dispatch(void)
{
    boot_flag_state s={.revision_word=0x121,.variant=2};
    assert(state_flag_dispatch_42d6c0_model(&s)==0);
    assert(s.state_200271b3==1&&s.state_200271b4==1&&s.state_200271b5==0);
    s.revision_word=0x122;s.variant=1;
    (void)state_flag_dispatch_42d6c0_model(&s);assert(s.state_200271b3==0&&s.state_200271b4==0&&s.state_200271b5==1);
    s.revision_word=0x123;s.variant=0;s.hw_state_word=0x2e000000;
    (void)state_flag_dispatch_42d6c0_model(&s);assert(s.state_200271b5==1);
    s.hw_state_word=0x32000000;
    (void)state_flag_dispatch_42d6c0_model(&s);assert(s.state_200271b5==0);
    s.hw_state_word=0x31940000;
    (void)state_flag_dispatch_42d6c0_model(&s);assert(s.state_200271b5==0);
    assert(startup_noop_42f670_model()==0U);
}
int main(void)
{
    test_gate_and_call_contract();test_read_errors_stop_before_commit();
    test_hw_state_composition();test_flag_dispatch();puts("startup handler model tests passed");return 0;
}
