#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

extern bool opencfw_em9305_packet_switch_known(uint8_t opcode, uintptr_t context,
                                                uintptr_t payload, uint32_t mode,
                                                uint32_t *status);
extern uint32_t opencfw_em9305_child_3191dc(uint32_t context,uint32_t packet,
                                             uint32_t mode);
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t context,
                                                    uintptr_t packet)
{
    (void)context;
    return (*(volatile uint8_t *)packet & 0x20u) ? 3u : 2u;
}
static unsigned child_calls;
static uint32_t child_arg, child_payload, child_third;
static uint8_t child_payload_byte;
static int child_state_mutation = -1;
static const char *child_name;
#define CHILD(name) uint32_t opencfw_em9305_packet_child_##name(uint32_t fields, uintptr_t payload, uint32_t third) \
    { ++child_calls; child_name=#name; child_arg=fields; child_payload=(uint32_t)payload; child_third=third; \
      child_payload_byte=*(volatile uint8_t *)(payload+1u); \
      if(child_state_mutation>=0) *(volatile uint8_t *)(uintptr_t)(fields-7u)=(uint8_t)child_state_mutation; \
      return 0x5a5a5a5au; }
CHILD(32dbe4) CHILD(32dc40) CHILD(32dd20) CHILD(32de08) CHILD(32deac)
CHILD(32dfe8) CHILD(32dffc) CHILD(32e068) CHILD(32e114) CHILD(32e128)
CHILD(32dba4)
CHILD(32de6c)
CHILD(32e1f4)
static uint32_t mask_result, mask_low, mask_high, mask_calls;
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high)
{ ++mask_calls; mask_low=low; mask_high=high; return mask_result; }

int main(void)
{
    assert(mmap((void *)0x800000u, 0x100000u, PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000u);
    child_state_mutation=-1;
    const uint8_t known[] = {2,3,4,5,6,7,10,11,17,18,19,26,27,29,30,34,35,36,37};
    unsigned cases=0;
    for (unsigned index=0;index<sizeof known;++index)
    for (unsigned enabled=0;enabled<2;++enabled)
    for (unsigned state_ok=0;state_ok<2;++state_ok) {
        uint8_t opcode=known[index];
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x801001u=0xa1u;
        *(volatile uint8_t *)0x801002u=0xb2u;
        *(volatile uint8_t *)0x801003u=0xc3u;
        *(volatile uint8_t *)0x801004u=0xd4u;
        *(volatile uint8_t *)0x805a94u=enabled?0xffu:0u;
        *(volatile uint8_t *)0x805a96u=enabled?0xffu:0u;
        *(volatile uint8_t *)0x805a97u=enabled?0xffu:0u;
        *(volatile uint8_t *)0x805a98u=enabled?0xffu:0u;
        uint8_t wanted=opcode==17?3u:opcode==26||opcode==29||opcode==30||opcode==2||opcode==7?2u:opcode==34||opcode==35?4u:5u;
        *(volatile uint8_t *)0x800005u=state_ok?wanted:0u;
        uint32_t result=0xbad0bad0u;
        assert(opencfw_em9305_packet_switch_known(opcode,0x800000u,0x801000u,0u,&result));
        bool default_only=opcode==3||opcode==4||opcode==5||opcode==6||opcode==10||opcode==11||opcode==18||opcode==19;
        bool gate=enabled||opcode==2||opcode==7;
        if (opcode==27) assert(result==(enabled?0u:25u));
        else assert(result==(default_only||!gate||!state_ok?25u:0u));
        if (default_only||opcode==27||!gate) assert(*(volatile uint8_t *)0x80000cu==0u);
        else if (opcode==26) {
            assert(*(volatile uint8_t *)0x80000cu==(0xa1u&31u));
            assert(*(volatile uint8_t *)0x80000du==(0xa1u>>6));
        } else {
            assert(*(volatile uint8_t *)0x80000cu==0xa1u);
            if (opcode!=2&&opcode!=7&&opcode!=29&&opcode!=30)
                assert(*(volatile uint8_t *)0x80000du==0xb2u);
            if (opcode==34||opcode==35||opcode==36||opcode==37)
                assert(*(volatile uint8_t *)0x80000eu==0xc3u);
            if (opcode==36||opcode==37)
                assert(*(volatile uint8_t *)0x80000fu==0xd4u);
        }
        ++cases;
    }
    const uint8_t called[] = {9,14,15,16,20,21,22,23,24,28,31,32,33,42};
    for (unsigned index=0;index<sizeof called;++index)
    for (unsigned enabled=0;enabled<2;++enabled)
    for (unsigned mode=0;mode<2;++mode) {
        uint8_t opcode=called[index];
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint32_t *)0x805a94u=enabled?0xffffffffu:0u;
        *(volatile uint8_t *)0x805a95u=enabled?0xffu:0u;
        *(volatile uint8_t *)0x805a97u=enabled?0xffu:0u;
        uint8_t state=opcode==15||opcode==16?24u:opcode==22||opcode==23?3u:
                      opcode==24?5u:opcode==28?35u:opcode==31?36u:
                      opcode==33?16u:opcode==42?43u:9u;
        *(volatile uint8_t *)0x800005u=state;
        *(volatile uint8_t *)0x801001u=0xa7u;
        child_calls=0u; child_arg=child_payload=child_third=0u;
        uint32_t result=0xbad0bad0u;
        assert(opencfw_em9305_packet_switch_known(opcode,0x800000u,0x801000u,mode,&result));
        bool gated=opcode==9||opcode==20||opcode==21 || (enabled &&
                    !(mode==1u&&(opcode==14||opcode==16||opcode==23||opcode==32)) &&
                    !(mode==0u&&(opcode==24||opcode==31||opcode==33)));
        assert(child_calls==(gated?1u:0u));
        assert(result==(gated?0u:25u));
        if (gated) {
            const char *expected=opcode==14||opcode==9?"32dfe8":
                opcode==15||opcode==16?"32de08":
                opcode==20||opcode==21?"32deac":
                opcode==22||opcode==23?"32e114":
                opcode==24?"32e128":opcode==28?"32dffc":
                opcode==31?"32dc40":opcode==32?"32dd20":
                opcode==33?"32dbe4":"32e068";
            assert(strcmp(child_name,expected)==0);
            assert(child_arg==0x80000cu);
            assert(child_payload==0x801000u && child_payload_byte==0xa7u);
            uint32_t third=(opcode==9||opcode==20||opcode==21)?mode:
                           opcode==31||opcode==32||opcode==33?0xffffffffu:0xffu;
            assert(child_third==third);
        }
        ++cases;
    }
    const uint8_t extended[] = {8,25,38,39,40,41};
    for (unsigned index=0;index<sizeof extended;++index)
    for (unsigned enabled=0;enabled<2;++enabled)
    for (unsigned mode=0;mode<2;++mode) {
        uint8_t opcode=extended[index];
        memset((void *)0x800000u,0,0x100000u);
        for (unsigned i=1;i<=10;++i)
            *(volatile uint8_t *)(uintptr_t)(0x801000u+i)=
                (uint8_t)(i==1?0xa1u:i==2&&opcode==25?0x30u:i);
        *(volatile uint8_t *)0x805a96u=enabled?0xffu:0u;
        *(volatile uint8_t *)0x805a98u=enabled?0xffu:0u;
        uint8_t state=opcode==8?9u:opcode==25?3u:opcode==40?4u:11u;
        *(volatile uint8_t *)0x800005u=state;
        uint32_t result=0xbad0bad0u;
        child_calls=0u;
        assert(opencfw_em9305_packet_switch_known(opcode,0x800000u,0x801000u,mode,&result));
        bool permitted=enabled && (opcode==8?mode!=0u:
                                    opcode==25?mode!=1u:
                                    opcode==38?mode!=1u:
                                    opcode==39?mode!=0u:
                                    opcode==41?mode!=1u:mode!=0u);
        if (opcode==8) {
            assert(child_calls==(mode!=0u));
            assert(result==(mode!=0u?0u:25u));
        } else {
            assert(child_calls==0u);
            if (!permitted) assert(result==25u && *(volatile uint8_t *)0x80000cu==0u);
            else if (opcode==25) {
                assert(*(volatile uint8_t *)0x80000cu==(0xa1u&7u));
                assert(*(volatile uint8_t *)0x80000du==0x30u);
                assert(result==30u);
            } else {
                assert(result==0u && *(volatile uint8_t *)0x80000cu==0xa1u);
                if (opcode==38||opcode==39)
                    assert(*(volatile uint16_t *)0x800014u==(uint16_t)(9u|10u<<8));
                if (opcode==41) {
                    assert(*(volatile uint8_t *)0x800015u==10u);
                    assert(*(volatile uint8_t *)0x800016u==0u);
                }
            }
        }
        ++cases;
    }
    for (unsigned mode=0;mode<2;++mode)
    for (unsigned state_ok=0;state_ok<2;++state_ok)
    for (unsigned high=0;high<2;++high)
    for (unsigned mask=0;mask<2;++mask) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x800005u=state_ok?8u:0u;
        *(volatile uint32_t *)0x80000cu=0xaabbccddu;
        *(volatile uint32_t *)0x800010u=high?32u:5u;
        child_calls=mask_calls=0u;
        mask_result=mask?2u:1u;
        uint32_t result=0xbad0bad0u;
        assert(opencfw_em9305_packet_switch_known(1u,0x800000u,0x801000u,mode,&result));
        assert(child_calls==(mode?1u:0u));
        if(mode) assert(strcmp(child_name,"32dba4")==0 && child_payload==0x801000u && child_third==mode);
        bool reached_mask=mode&&state_ok&&!high;
        assert(mask_calls==(reached_mask?1u:0u));
        if (reached_mask) assert(mask_low==0xaabbccddu&&mask_high==5u);
        assert(result==(!mode||!state_ok?25u:high||!mask?30u:0u));
        ++cases;
    }
    for (unsigned failure=0;failure<10;++failure) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x800005u=12u;
        *(volatile uint8_t *)0x80000cu=1u;
        *(volatile uint16_t *)0x80000eu=2000u;
        *(volatile uint16_t *)0x800010u=3000u;
        *(volatile uint16_t *)0x800012u=1u;
        *(volatile uint16_t *)0x800014u=3000u;
        uint32_t mode=1u;
        switch(failure) {
        case 1:mode=0u;break;
        case 2:*(volatile uint8_t *)0x800005u=1u;break;
        case 3:*(volatile uint16_t *)0x800010u=3201u;break;
        case 4:*(volatile uint8_t *)0x80000cu=0u;break;
        case 5:*(volatile uint8_t *)0x80000cu=9u;break;
        case 6:*(volatile uint16_t *)0x80000eu=3001u;break;
        case 7:*(volatile uint16_t *)0x800014u=3201u;break;
        case 8:*(volatile uint16_t *)0x800012u=500u;break;
        case 9:*(volatile uint16_t *)0x800014u=1000u;break;
        }
        child_calls=0u;
        uint32_t result=0xbad0bad0u;
        assert(opencfw_em9305_packet_switch_known(0u,0x800000u,0x801000u,mode,&result));
        assert(child_calls==(mode?1u:0u));
        if(mode) assert(strcmp(child_name,"32de6c")==0 && child_payload==0x801000u && child_third==mode);
        assert(result==(failure==0u?0u:failure==1u||failure==2u?25u:30u));
        ++cases;
    }
    /* Native R1 and post-child context read are live effects, not inert arguments. */
    for (unsigned mutation=0;mutation<2;++mutation) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x801001u=0x5du;
        *(volatile uint8_t *)0x800005u=9u;
        child_state_mutation=mutation?9:3;
        child_calls=0u;
        uint32_t result=99u;
        assert(opencfw_em9305_packet_switch_known(9u,0x800000u,0x801000u,0x41u,&result));
        assert(child_calls==1u && child_payload==0x801000u && child_payload_byte==0x5du);
        assert(child_third==0x41u && result==(mutation?0u:25u));
        ++cases;
    }
    child_state_mutation=-1;
    /* EXTH/EXTB are unsigned, and the final product branch compares signed words. */
    for (unsigned first_case=0;first_case<4;++first_case) {
        static const uint16_t values[]={0u,6u,9u,3201u};
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x800005u=12u;
        *(volatile uint8_t *)0x80000cu=1u;
        *(volatile uint16_t *)0x80000eu=0u;
        *(volatile uint16_t *)0x800010u=values[first_case];
        *(volatile uint16_t *)0x800012u=0u;
        *(volatile uint16_t *)0x800014u=10u;
        uint32_t result=99u;
        assert(opencfw_em9305_packet_switch_known(0u,0x800000u,0x801000u,1u,&result));
        assert(result==(first_case==1u||first_case==2u?0u:30u));
        ++cases;
    }
    for (unsigned second_case=0;second_case<4;++second_case) {
        static const uint8_t values[]={0u,1u,0x25u,0x26u};
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x805a96u=1u;
        *(volatile uint8_t *)0x800005u=3u;
        *(volatile uint8_t *)0x801001u=1u;
        *(volatile uint8_t *)0x801002u=values[second_case];
        uint32_t result=99u;
        assert(opencfw_em9305_packet_switch_known(25u,0x800000u,0x801000u,0u,&result));
        assert(result==(second_case==2u?0u:30u));
        ++cases;
    }
    for (unsigned header=0;header<2;++header)
    for (unsigned opcode=0;opcode<43;++opcode) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x801000u=header?0x20u:0u;
        *(volatile uint8_t *)(uintptr_t)(0x801002u+header)=(uint8_t)opcode;
        uint32_t result=opencfw_em9305_child_3191dc(0x800000u,0x801000u,0u);
        assert(result==25u);
        assert(*(volatile uint8_t *)0x800008u==opcode);
        ++cases;
    }
    for (unsigned invalid=43;invalid<=255;invalid+=212) {
        memset((void *)0x800000u,0,0x100000u);
        *(volatile uint8_t *)0x801002u=(uint8_t)invalid;
        assert(opencfw_em9305_child_3191dc(0x800000u,0x801000u,0u)==25u);
        assert(*(volatile uint8_t *)0x800008u==(uint8_t)invalid);
        ++cases;
    }
    uint32_t sentinel=0xabba1234u;
    assert(!opencfw_em9305_packet_switch_known(43u,0x800000u,0x801000u,0u,&sentinel));
    assert(sentinel==0xabba1234u);
    printf("PASS packet known switch %u state/gate fixtures; unresolved route explicit\n",cases);
    return 0;
}
