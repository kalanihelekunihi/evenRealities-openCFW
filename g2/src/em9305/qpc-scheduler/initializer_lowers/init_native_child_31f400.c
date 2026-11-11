#include <stdint.h>

/* Native 0x31f400..0x31f50c: periodic-sync report handler. Without data
 * the sync context (object +36) is dropped (325688). Otherwise the report
 * header at 0x803b68 is decoded from the PDU (32db0c into +12, 32df24 flags
 * into +10/+11, ready byte +9); on the first report (+701 clear) the
 * address-type bits 0x26 are cleared from the flags and the context's
 * advertiser type byte (+154) when filtering is on (+153), and always
 * when all three low type bits are set. After 3256c8 runs, the peer
 * address (+156..+168), the decoded header (kind, id) and type form a 20-byte request for 30301c on
 * the scanner (object +44, filter +76, list +144); a match of an
 * unfiltered context whose address (+104/+108) equals the list entry
 * publishes the PHY options (+64 & 0x17 | 8) at 0x803b92, anything else
 * marks the report rejected (0x803b69). Returns 0. */
extern uintptr_t opencfw_em9305_child_3256c8(uintptr_t link);
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out,uintptr_t in);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out,
    uintptr_t flags_out,uintptr_t in);
extern uint32_t opencfw_em9305_child_325688(uintptr_t record);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request,uintptr_t filter,
                                            uint32_t flags,uintptr_t list);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_child_31f400(uintptr_t object,uintptr_t data)
{
    uintptr_t context=r32(object+36u);
    if(data==0u){
        (void)opencfw_em9305_child_325688(context);
        return 0u;
    }
    uintptr_t scanner=r32(object+44u);
    (void)opencfw_em9305_child_3256c8(context);
    uintptr_t peer=context+156u;
    uint32_t used=opencfw_em9305_child_32db0c(0x803b74u,data);
    uint32_t flags_status=opencfw_em9305_dispatch_child_32df24(context+152u,
                                                               0x803b72u,data+used);
    uintptr_t first=context+701u;
    w8(0x803b73u,flags_status);
    w8(0x803b71u,1u);
    uint32_t type;
    if(r8(first)!=0u){
        type=r8(context+154u);
    }else{
        if(r8(context+153u)!=0u){
            uint32_t flags=r8(0x803b72u);
            uint32_t stored=r8(context+154u);
            w8(first,1u);
            flags&=~0x26u;
            type=stored&~0x26u;
            w8(0x803b72u,flags);
            w8(context+154u,type);
        }else{
            type=r8(context+154u);
        }
        if((type&7u)==7u){
            uint32_t flags=r8(0x803b72u);
            type&=0xd9u;
            w8(first,1u);
            flags&=~0x26u;
            w8(context+154u,type);
            w8(0x803b72u,flags);
        }
    }
    _Alignas(4) uint8_t request[20];
    uint32_t a=r32(peer),c=r32(peer+8u);
    uint32_t kind=r8(0x803b74u);
    uint32_t sid=*(volatile uint16_t *)0x803b76u;
    uintptr_t current=r32(object+44u);
    uint32_t b=r32(peer+4u),d=r32(peer+12u);
    *(uint32_t *)(void *)request=a;
    uintptr_t list=scanner+144u;
    *(uint32_t *)(void *)(request+8)=c;
    request[16]=(uint8_t)kind;
    *(uint16_t *)(void *)(request+18)=(uint16_t)sid;
    request[17]=(uint8_t)type;
    *(uint32_t *)(void *)(request+4)=b;
    *(uint32_t *)(void *)(request+12)=d;
    if(opencfw_em9305_child_30301c((uintptr_t)request,current+76u,0u,list)!=0u
       &&(r8(context+153u)&3u)==0u
       &&((r32(list+4u)^r32(context+108u))|(r32(list)^r32(context+104u)))==0u){
        uint32_t options=*(volatile uint16_t *)(context+64u);
        *(volatile uint16_t *)0x803b92u=(uint16_t)((options&0x17u)|8u);
        return 0u;
    }
    w8(0x803b69u,1u);
    return 0u;
}
