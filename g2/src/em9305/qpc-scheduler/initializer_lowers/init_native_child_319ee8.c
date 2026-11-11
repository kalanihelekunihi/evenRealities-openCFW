#include <stdint.h>

/* Native 0x319ee8..0x31a1b0: build an advertising report record (36 bytes
 * at report) for a received PDU unless the link is busy (+56). The record
 * gets the event type (mode, bit 4 legacy plus the PDU-type bits), the
 * advertiser address type/address (+6/+7), the RSSI 0x7f (+16), TX power
 * 0xff (+15), primary PHY (+13: 1, or 3/4 for coded with the LE coded
 * option bit 9 of 0x805a98 and link +445), the signed power (+17) and the
 * data pointer/length (+32/+28). Legacy PDUs (header type 0..6, length
 * 6..37) set the type bits through a jump table (ADV_IND 0x13,
 * ADV_DIRECT_IND 0x15 with the resolved target address at +20/+21 via
 * 3039a0, ADV_NONCONN_IND 0x10, SCAN_RSP 0x1a plus bit 0 when not
 * scanning actively (0x803b68), ADV_SCAN_IND 0x12); extended PDUs (7, 8)
 * use the cached extended header at link +148.. (flags +154/+153, SID,
 * TX power, periodic interval, secondary PHY from +204) and, when TargetA
 * is present or link +701 is set, the target address (+20/+21), clearing
 * +701. Returns 1 when a report was built, 0 otherwise. */
extern void *opencfw_em9305_memset(void *destination,int value,uint32_t bytes);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,
    uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_radio_identity_compare_3039a0(uint32_t low,
    uint32_t high,uint32_t type,uint32_t peer_low,uint32_t peer_high);
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

/* Target address (+20 type, +21 address) for a directed advertiser address
 * low/high: a resolvable private address that resolves (3039a0) is
 * reported as the own identity (3 for random, 2 for public, by link +13)
 * or as 0xfe unresolved; otherwise the own address by link +13 (1 random,
 * 0 public). */
static void report_target(uintptr_t link,uintptr_t report,uint32_t low,
                          uint32_t high,uint32_t type,uint32_t peer_low,
                          uint32_t peer_high)
{
    uint32_t kind;
    if((high&0xc000u)==0x4000u){
        if(opencfw_em9305_radio_identity_compare_3039a0(low,high,type&~2u,
               peer_low,peer_high)==0u){
            kind=0xfeu;
        }else if((r8(link+13u)|2u)==3u){
            kind=3u;
            high=r32(0x805a90u);
            low=r32(0x805a8cu);
        }else{
            high=r32(0x805b44u);
            low=r32(0x805b40u);
            kind=2u;
        }
    }else if(r8(link+13u)==1u){
        kind=1u;
        high=r32(0x805a90u);
        low=r32(0x805a8cu);
    }else{
        high=r32(0x805b44u);
        low=r32(0x805b40u);
        kind=0u;
    }
    (void)opencfw_em9305_radio_address_write_3045e8(report+21u,low,high);
    w8(report+20u,kind);
}

uint32_t opencfw_em9305_child_319ee8(uintptr_t link,uint32_t mode,
    uintptr_t header,uint32_t low,uint32_t high,uint32_t type,int32_t power,
    uintptr_t pdu,uintptr_t report)
{
    if(r8(link+56u)!=0u)return 0u;
    (void)opencfw_em9305_memset((void *)report,0,0x24u);
    uint32_t primary=r8(link+16u);
    uint32_t options=r32(0x805a98u);
    w8(report+17u,(uint32_t)power);
    w8(report+15u,0xffu);
    w16(report+4u,mode);
    w8(report+16u,0x7fu);
    if(primary==2u){
        if((options&0x200u)!=0u&&r8(link+445u)==1u)w8(report+13u,4u);
        else w8(report+13u,3u);
    }else if(primary==0u){
        w8(report+13u,1u);
    }
    uint32_t pdu_type=r8(header);
    if(pdu_type-7u<2u){
        uintptr_t ext=link+148u;
        uint32_t flags=r8(link+154u);
        if((flags&1u)!=0u){
            w8(report+6u,type);
            (void)opencfw_em9305_radio_address_write_3045e8(report+7u,low,high);
            mode=r16(report+4u);
            flags=r8(link+154u);
        }else{
            w8(report+6u,0xffu);
        }
        uint32_t mode_bits=r8(link+153u);
        uint32_t data=r32(ext);
        uint32_t secondary=r8(ext+56u);
        uint32_t coded_s8=0u;
        w16(report+28u,0u);
        w32(report+32u,data);
        w16(report+4u,((flags<<1)&4u)|(mode_bits&3u)|mode);
        if((options&0x200u)!=0u)coded_s8=r8(link+666u);
        uint32_t phy;
        if(secondary==2u)phy=(coded_s8==1u)+3u;
        else if(secondary==1u)phy=2u;
        else phy=1u;
        w8(report+14u,phy);
        if((flags&8u)!=0u)w8(report+15u,r8(ext+28u));
        if((flags&0x40u)!=0u)w8(report+16u,r8(link+177u));
        if((flags&0x20u)!=0u)w16(report+18u,r16(ext+64u));
        if((flags&2u)==0u&&r8(link+701u)==0u)return 1u;
        uint32_t target_high=r32(ext+20u);
        report_target(link,report,r32(ext+16u),target_high,type,low,high);
        w8(link+701u,0u);
        return 1u;
    }
    uint32_t length=r8(header+4u);
    if((uint8_t)(length-38u)<224u)return 0u;
    w16(report+4u,mode|0x10u);
    if(pdu_type>=7u)return 0u;
    uint32_t data_length=length-6u;
    pdu+=8u;
    switch(pdu_type){
    case 0u:
        w16(report+4u,mode|0x13u);
        break;
    case 1u:{
        w16(report+4u,mode|0x15u);
        uint64_t target=opencfw_em9305_controller_pack_address(pdu);
        report_target(link,report,(uint32_t)target,(uint32_t)(target>>32),
                      type,low,high);
        data_length=0u;
        break;
    }
    case 2u:
        break;
    case 4u:
        w16(report+4u,mode|(r8(0x803b68u)==0u)|0x1au);
        break;
    case 6u:
        w16(report+4u,mode|0x12u);
        break;
    default:
        return 0u;
    }
    w8(report+6u,type);
    (void)opencfw_em9305_radio_address_write_3045e8(report+7u,low,high);
    w32(report+32u,pdu);
    w16(report+28u,(uint8_t)data_length);
    return 1u;
}
