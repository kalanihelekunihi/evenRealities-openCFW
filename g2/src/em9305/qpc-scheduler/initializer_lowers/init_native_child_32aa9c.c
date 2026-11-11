#include <stdint.h>

/* Native 0x32aa9c..0x32ad38: advertising event completion for the set
 * (object +36) and its PDU object (+44). A set that is not running
 * (+2785) counts the event (+825, unless +2787), and ends with status 4
 * (325a40, +2262 set) when terminating (+2262/+2260) or when the maximum
 * event count (+824) is reached (status 0x43 at +826). Otherwise the
 * advertising PDU is rebuilt: the channel index (+15, default 0x805bed)
 * is copied to +14; for legacy sets pending data (+1440, length +1441,
 * DID +1442) is installed into the data buffer (*(+1424) <- +1444) and
 * the PDU is composed by the host hook (*0x805174, for event property bit
 * 7) or 32387c, its length stored at +124; a pending start (32841c) and a
 * deferred DID update (+2786) are then applied. Extended sets refresh
 * their resolvable addresses (new local RPA on request at +3 when
 * 0x805be2 is 1, or a resolved peer pair when bit 1 of 0x805be2 is set,
 * copied to +842/+908 and the PDU +84/+88; peer identity into +848 and
 * +24/+28 for directed sets with bits 0x44 at +80), and copy pending AUX
 * data (+1440/+1441 into *(+100) for PDU types 0, 2, 6; +1716/+1717 from
 * +1718 into *(+108)) with lengths at +124/+125. Finally the object is
 * rescheduled (312918, 32ad68). */
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_child_325a40(uintptr_t record,uint32_t status);
extern uint32_t opencfw_em9305_child_32387c(uintptr_t record,uintptr_t output,
                                            uint32_t count);
extern uint32_t opencfw_em9305_child_32841c(uintptr_t record);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,
    uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t kind,uint32_t low,
    uint32_t high,uintptr_t output);
extern uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t kind,
    uint32_t low,uint32_t high,uintptr_t output);
extern void opencfw_em9305_associated_object_init_312918(uintptr_t object,
                                                         uint32_t length);
extern void opencfw_em9305_child_32ad68(uintptr_t context);
typedef uint32_t (*opencfw_em9305_compose_hook_t)(uintptr_t,uintptr_t,uintptr_t,
                                                  uint32_t);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

static void set_local_address(uintptr_t set,uintptr_t pdu,uint32_t low,
                              uint32_t high)
{
    (void)opencfw_em9305_radio_address_write_3045e8(set+842u,low,high);
    (void)opencfw_em9305_memcpy((void *)(set+908u),(const void *)(set+842u),6u);
    w32(pdu+88u,high);
    w32(pdu+84u,low);
}

void opencfw_em9305_child_32aa9c(uintptr_t object)
{
    uintptr_t set=r32(object+36u);
    uintptr_t pdu=r32(object+44u);
    uintptr_t running=set+0xae1u;
    if(r8(running)==0u){
        if(r8(set+0xae3u)==0u)w8(set+825u,r8(set+825u)+1u);
        uintptr_t terminate=set+0x8d6u;
        uint32_t stop=1u;
        if(r8(terminate)==0u&&r8(set+0x8d4u)==0u){
            uint32_t limit=r8(set+824u);
            if(limit==0u||r8(set+825u)<limit)stop=0u;
            else w8(set+826u,0x43u);
        }
        if(stop){
            w8(terminate,1u);
            (void)opencfw_em9305_child_325a40(set,4u);
            return;
        }
    }
    uint32_t channel=r8(pdu+15u);
    if(channel==0u)channel=r8(0x805bedu);
    w8(pdu+14u,channel);
    uint32_t properties=r16(set+32u);
    uintptr_t data=set+0x5a0u;
    pdu=r32(object+44u);
    if((properties&0x10u)==0u){
        uint32_t copied=r8(data);
        if(copied!=0u){
            uintptr_t buffer=r32(data-16u);
            uint32_t length=r8(data+1u);
            w8(data,0u);
            (void)opencfw_em9305_memcpy((void *)buffer,(const void *)(set+1444u),length);
            length=r8(data+1u);
            uint32_t did=r16(data+2u);
            uint32_t extra=r8(data+255u);
            properties=r16(set+32u);
            w16(set+0x8cau,length);
            w16(data-20u,length);
            w16(set+64u,did);
            w8(data-8u,extra);
        }
        if((properties&0x80u)==0u){
            w8(pdu+124u,opencfw_em9305_child_32387c(set,set+840u,0u));
        }else{
            uintptr_t hook=r32(0x805174u);
            if(hook!=0u)
                w8(pdu+124u,((opencfw_em9305_compose_hook_t)hook)(set,set+840u,
                                                                  set+1972u,0u));
        }
        if(copied!=0u&&r8(running)==0u&&r32(set+828u)!=0u){
            (void)opencfw_em9305_child_32841c(set);
            w8(running,1u);
        }
        if(r8(set+378u)!=0u&&r8(set+369u)!=0u&&r32(set+828u)!=0u
           &&r8(running)==0u){
            w8(set+378u,0u);
            (void)opencfw_em9305_child_32841c(set);
            w8(running,1u);
        }
        if(r8(set+0xae2u)!=0u&&r8(running)==0u){
            uint32_t did=r16(data+2u);
            w8(set+0xae2u,0u);
            w16(set+64u,did);
        }
    }else{
        uint32_t request=r8(set+3u);
        uint32_t privacy=r8(0x805be2u);
        if(request!=0u&&privacy==1u){
            uint32_t high=r32(set+12u),low=r32(set+8u);
            w8(set+3u,0u);
            w32(set+20u,high);
            w32(set+16u,low);
            set_local_address(set,pdu,low,high);
        }else if((privacy&2u)!=0u){
            uint32_t pair[2];
            if(opencfw_em9305_radio_peer_pair_303a40(r8(set+58u),r32(set+48u),
                   r32(set+52u),(uintptr_t)pair)!=0u){
                uint32_t high=pair[1],low=pair[0];
                w32(set+20u,high);
                w32(set+16u,low);
                w32(0x805be8u,high);
                w32(0x805be4u,low);
                set_local_address(set,pdu,low,high);
            }
        }
        if((r8(set+32u)&4u)!=0u&&(r32(pdu+80u)&0x44u)==0x44u){
            uint32_t pair[2];
            if(opencfw_em9305_radio_identity_pair_303a60(r8(set+58u),r32(set+48u),
                   r32(set+52u),(uintptr_t)pair)!=0u){
                (void)opencfw_em9305_radio_address_write_3045e8(set+848u,pair[0],
                                                               pair[1]);
                w32(set+28u,pair[1]);
                w32(set+24u,pair[0]);
            }
        }
        if(r8(data)!=0u){
            w8(data,0u);
            uintptr_t aux=r32(pdu+100u);
            uint32_t type=r8(aux)&15u;
            if(type<7u&&((0x45u>>type)&1u)!=0u){
                w8(pdu+124u,r8(data+1u)+8u);
                w8(aux+1u,r8(data+1u)+6u);
                (void)opencfw_em9305_memcpy((void *)(r32(pdu+100u)+8u),
                                            (const void *)(set+1442u),r8(data+1u));
            }
        }
        if(r8(set+1716u)!=0u){
            uint32_t length=r8(set+1717u);
            w8(set+1716u,0u);
            w8(pdu+125u,length+8u);
            uint32_t header=r8(set+1717u)+6u;
            uintptr_t chain=r32(pdu+108u);
            w8(chain+1u,header);
            (void)opencfw_em9305_memcpy((void *)(r32(pdu+108u)+8u),
                                        (const void *)(set+1718u),r8(set+1717u));
        }
    }
    opencfw_em9305_associated_object_init_312918(object,0u);
    opencfw_em9305_child_32ad68(object);
}
