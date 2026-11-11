#include <stdint.h>

/* Native 0x32cbf0..0x32ccdc: power-control request handler. The PHY bit
 * (0x80281c) selects PHY index 1..4 (255 when not a single known bit);
 * an invalid PHY sets status 0x20 (+747) and a power of 0x7e (0x80281e)
 * sets status 30. Otherwise a changed remote power for that PHY (+553 +
 * index) is reported through 323620 when reporting is on (+768), the new
 * power is stored, the local adjustment (317214, delta 0x80281d) is kept
 * at +764 with the PHY index at +766 and, when non-zero with local
 * reporting on (+767), the local power for the current PHY (+332 table;
 * index 4 uses the coded entry) is reported as well. */
extern uint32_t opencfw_em9305_command_kind_valid_31b768(uint32_t kind);
extern uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t value);
extern uint32_t opencfw_em9305_callback_323620(uintptr_t record,uint32_t status,
    uint32_t kind,uint32_t index,int32_t previous,uint32_t current,int32_t phy);
extern int32_t opencfw_em9305_child_317214(uintptr_t record,uint32_t phy,
                                           int32_t delta);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

void opencfw_em9305_child_32cbf0(uintptr_t record)
{
    uintptr_t status=record+747u;
    uint32_t bit=r8(0x80281cu);
    int32_t power=*(volatile int8_t *)0x80281eu;
    w8(status,0u);
    uint32_t phy=0xffu;
    for(uint32_t candidate=1u;candidate<=4u;++candidate){
        if((1u<<(candidate-1u))==bit){
            phy=candidate;
            break;
        }
    }
    uint32_t index=(uint8_t)phy;
    if(index==255u||opencfw_em9305_command_kind_valid_31b768(index)==0u){
        w8(status,0x20u);
        return;
    }
    if(power==0x7e){
        w8(status,30u);
        return;
    }
    uintptr_t remote=record+index+553u;
    if(r8(record+768u)!=0u&&r8(remote)!=(uint8_t)power){
        uint32_t level=opencfw_em9305_ll_signed_classify_31b374((uint32_t)power);
        int32_t change=(int8_t)((uint32_t)power-r8(remote));
        (void)opencfw_em9305_callback_323620(record,0u,1u,index,power,level,change);
    }
    w8(remote,(uint32_t)power);
    int32_t delta=*(volatile int8_t *)0x80281du;
    int32_t adjust=opencfw_em9305_child_317214(record,index,delta);
    w8(record+766u,phy);
    w8(record+764u,(uint32_t)adjust);
    if(adjust==0||r8(record+767u)==0u)return;
    uint32_t mode=index==4u?3u:phy;
    uint32_t slot=(uint8_t)mode-(((uint8_t)mode!=3u)|(index!=4u));
    int32_t local=*(volatile int8_t *)(record+332u+slot);
    uint32_t level=opencfw_em9305_ll_signed_classify_31b374((uint32_t)local);
    (void)opencfw_em9305_callback_323620(record,0u,0u,index,local,level,
                                         *(volatile int8_t *)(record+764u));
}
