#include <stdint.h>

/* Native 0x32ce24..0x32ce84: latch the current command's PHY bytes (+4,
 * +5 of 0x805c6c) into the record at +764/+766. A 0x7e placeholder in
 * the per-PHY slot (+331+phy) is replaced by the configured default
 * (+40 of 0x805cac), which for coded PHYs (>=3) is also stored in slot
 * +335 (phy 3) or +334. With no PHY change pending (+771) and a zero
 * first byte, set the report byte at +745. */
void opencfw_em9305_child_32ce24(uintptr_t record)
{
    uintptr_t command=*(volatile uint32_t *)(uintptr_t)0x805c6cu;
    uint32_t first=*(volatile uint8_t *)(command+4u);
    *(volatile uint8_t *)(record+764u)=(uint8_t)first;
    uint32_t phy=*(volatile uint8_t *)(command+5u);
    volatile uint8_t *slot=(volatile uint8_t *)(record+phy+331u);
    uint32_t current=*slot;
    *(volatile uint8_t *)(record+766u)=(uint8_t)phy;
    if(current==0x7eu){
        *slot=*(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u);
        if(phy>=3u){
            uint32_t index=(phy==3u)?3u:2u;
            *(volatile uint8_t *)(record+index+332u)=
                *(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+40u);
        }
    }
    if((*(volatile uint8_t *)(record+771u)|first)==0u)
        *(volatile uint8_t *)(record+745u)=1u;
}
