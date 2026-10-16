#include <stdint.h>

/* Complete native 0x31affc..0x31b21a. Three compact inline branch tables
 * are expressed as event classifications; no executable bytes are copied. */
static uint8_t b(uintptr_t p){return *(volatile uint8_t *)p;}
static uint32_t w(uintptr_t p){return *(volatile uint32_t *)p;}
static void sb(uintptr_t p,uint8_t v){*(volatile uint8_t *)p=v;}
static void sw(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}

static uint32_t event_112(uintptr_t context)
{
    if(b(context+1u)==3u) return 255u;
    uint32_t primary=w(context+652u);
    if((primary&1u)!=0u) {
        sw(context+656u,0u);
        sw(context+652u,primary&~1u);
        return 0u;
    }
    uint32_t secondary=w(context+644u);
    if((secondary&1u)!=0u) {
        sw(context+648u,0u);
        sw(context+644u,secondary&~1u);
        return 0u;
    }
    for(uint32_t index=0u;index<10u;index++) {
        if((primary&(1u<<index))!=0u) {
            sw(context+656u,0u);
            sw(context+652u,primary&~(1u<<index));
            return index;
        }
    }
    for(uint32_t index=0u;index<10u;index++) {
        if((secondary&(1u<<index))!=0u) {
            uint32_t byte631=b(context+631u);
            sw(context+648u,0u);
            sw(context+644u,secondary&~(1u<<index));
            if(byte631!=0u) {
                uint32_t byte626=b(context+626u);
                sb(context+631u,0u);
                if(byte626!=0u) sb(context+620u,1u);
                sb(context+635u,(uint8_t)index);
            }
            return index;
        }
    }
    return 255u;
}

static uint32_t event_twelve_secondary(void)
{
    uint32_t code=b(0x80281cu);
    if(code>=20u && code<42u) {
        switch(code) {
        case 20u:case 21u:return 4u;
        case 29u:case 30u:return 7u;
        case 35u:case 36u:return 28u;
        case 37u:return 27u;
        case 40u:return 8u;
        case 41u:return 9u;
        default:return 255u;
        }
    }
    switch(code) {
    case 1u:return 1u;
    case 2u:return 0u;
    case 8u:case 9u:case 14u:return 2u;
    case 12u:return 3u;
    default:return 255u;
    }
}

uint32_t opencfw_em9305_mode_selector_31affc(uintptr_t context,
                                                uint32_t event)
{
    uint32_t offset=event-22u;
    if(offset<14u) {
        switch(offset) {
        case 0u:return 1u;
        case 1u:return 0u;
        case 5u:return 2u;
        case 6u:return 3u;
        case 9u:return 4u;
        case 11u:return 5u;
        case 12u:return 6u;
        case 13u:return 7u;
        default:return 255u;
        }
    }
    offset=event-102u;
    if(offset<11u) {
        switch(offset) {
        case 0u:return 3u;
        case 1u:return 2u;
        case 2u:return 4u;
        case 4u:return 0u;
        case 5u:return 9u;
        case 6u:return 8u;
        case 8u:return b(context+635u);
        case 10u:return event_112(context);
        default:return 255u;
        }
    }
    if(event!=12u) return 255u;
    uint32_t code=b(0x802818u)-1u;
    if(code>=42u) return 255u;
    switch(code) {
    case 0u:return 1u;
    case 1u:return 0u;
    case 6u:return event_twelve_secondary();
    case 7u:case 8u:case 13u:return 2u;
    case 11u:return 3u;
    case 12u:case 16u:return b(context+635u);
    case 19u:case 20u:return 4u;
    case 24u:return 5u;
    case 27u:return 6u;
    case 28u:case 29u:return 7u;
    case 39u:return 8u;
    case 40u:return 9u;
    case 41u:return 6u;
    default:return 255u;
    }
}
