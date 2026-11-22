#include <stdint.h>

/* Native 0x317214..0x317280: step the per-PHY transmit power slot
 * (+332 + PHY index) by delta. 0x7f marks an unsupported PHY (returns 0),
 * 0x7e takes the configured default (+40 of 0x805cac); otherwise the
 * radio power level is looked up. A positive step below the maximum
 * saturates at 0x7f. The 310200-normalised level is stored back (and in
 * +66 for the active PHY, +76); returns the change against the level. */
extern uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t level);
extern int32_t opencfw_em9305_child_310200(int32_t level);

int32_t opencfw_em9305_child_317214(uintptr_t record, uint32_t phy, int32_t delta)
{
    int32_t clamped=(int32_t)phy<3?(int32_t)phy:3;
    volatile uint8_t *slot=(volatile uint8_t *)(record+332u+(uint32_t)clamped-(phy<4u));
    int32_t current=(int8_t)*slot;
    uint32_t base,reference;
    if(current==0x7f)return 0;
    if(current==0x7e){
        base=*(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u);
        reference=base;
    }else{
        reference=opencfw_em9305_ll_signed_clamp_310230((uint32_t)current);
        base=*slot;
    }
    int32_t level=(int8_t)(base+(uint32_t)delta);
    if(delta>=1&&level<(int8_t)reference)level=0x7f;
    level=opencfw_em9305_child_310200(level);
    *slot=(uint8_t)level;
    if((uint32_t)clamped==*(volatile uint8_t *)(record+76u))
        *(volatile uint8_t *)(record+66u)=(uint8_t)level;
    return (int8_t)((uint32_t)level-reference);
}
