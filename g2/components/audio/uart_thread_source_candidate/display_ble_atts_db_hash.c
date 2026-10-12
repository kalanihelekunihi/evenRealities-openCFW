/* Native AttsCalculateDbHash 0x53527c; pinned Cordio atts_main.c.
 * Native build has the WSF_ASSERT(FALSE) path compiled out. */
#include <stdint.h>
extern uint8_t audio_ble_atts_state[]; /* selected native attsCb 0x2006e5f0 */
extern uint16_t attsIsHashableAttr(const uint8_t *attribute);
extern void *WsfBufAlloc(uint16_t length);
extern uint8_t AttsHashDatabaseString(uint8_t *key,uint8_t *message,uint16_t length);

static uint8_t *pointer_at(const uint8_t *p)
{
    uint32_t raw;
    __builtin_memcpy(&raw,p,4u);
    return (uint8_t *)(uintptr_t)raw;
}
static uint16_t half_at(const uint8_t *p)
{
    return (uint16_t)p[0]|((uint16_t)p[1]<<8u);
}

void AttsCalculateDbHash(void)
{
    uint16_t length=0u;
    uint8_t *group=pointer_at(audio_ble_atts_state+0x258u);
    for (uint8_t *g=group;g;g=pointer_at(g)) {
        uint8_t *attribute=pointer_at(g+4u);
        uint8_t count=(uint8_t)(half_at(g+0x12u)-half_at(g+0x10u)+1u);
        while (count--) {
            length=(uint16_t)(length+attsIsHashableAttr(attribute));
            attribute+=0x10u;
        }
    }
    uint8_t *message=WsfBufAlloc(length);
    if (!message) return;
    uint8_t key[16]={0};
    uint8_t *out=message;
    for (uint8_t *g=group;g;g=pointer_at(g)) {
        uint8_t *attribute=pointer_at(g+4u);
        uint16_t handle=half_at(g+0x10u);
        const uint16_t end=half_at(g+0x12u);
        while (handle<=end) {
            uint16_t value_length=attsIsHashableAttr(attribute);
            if (value_length!=0u) {
                *out++=(uint8_t)handle;
                *out++=(uint8_t)(handle>>8u);
                const uint8_t *uuid=pointer_at(attribute);
                uint8_t uuid_length=2u;
                if (attribute[0x0eu]&1u) {
                    __builtin_memcpy(out,uuid,16u);out+=16u;uuid_length=16u;
                } else {
                    *out++=uuid[0];*out++=uuid[1];
                }
                if (value_length!=(uint16_t)(uuid_length+2u)) {
                    const uint16_t n=half_at(pointer_at(attribute+8u));
                    __builtin_memcpy(out,pointer_at(attribute+4u),n);
                    out+=n;
                }
            }
            attribute+=0x10u;
            handle++;
        }
    }
    (void)AttsHashDatabaseString(key,message,length);
}
