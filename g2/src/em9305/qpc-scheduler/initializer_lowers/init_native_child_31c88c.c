#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31c88c..0x31c98e: initialise the link's advertising/initiating
 * block (+484, 216 bytes): completion callbacks (31c990 twice, 320b3c,
 * 320d68), owner, channel/access defaults (access address 0x8e89bed6,
 * CRC init 0x555555, 384 us windows, the second one only for PHY modes
 * 1, 3 and 4 of +98), the clock-accuracy byte (((uintptr_t)&em9305_ram_805a6c + 0x30u)) and the own
 * address: the static (((uintptr_t)&em9305_ram_805af0 + 0x50u)) or public (((uintptr_t)&em9305_ram_805a6c + 0x20u)) one by bit 0 of
 * +99, with address-type flags (+612) extended by 0x51 when resolution is
 * enabled (((uintptr_t)&em9305_ram_805a6c + 0x31u)) and, for PHY mode 0, by the peer address type and
 * the peer address (+624/+628). Clears the state bytes and returns 0. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern uint32_t opencfw_em9305_child_31c990(uintptr_t object);
extern uint32_t opencfw_em9305_child_320b3c(uintptr_t object);
extern uint32_t opencfw_em9305_child_320d68(uintptr_t context,uintptr_t pdu);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}

uint32_t opencfw_em9305_child_31c88c(uintptr_t link,uint32_t unused,
                                     uint32_t peer_low,uint32_t peer_high,
                                     uint32_t peer_type)
{
    (void)unused;
    (void)opencfw_em9305_memset((void *)(link+484u),0u,216u);
    uint32_t mode=r8(link+98u);
    uint32_t done=(uint32_t)(uintptr_t)opencfw_em9305_child_31c990;
    w32(link+516u,done);
    w32(link+512u,done);
    uint32_t accuracy=r8(((uintptr_t)&em9305_ram_805a6c + 0x30u));
    w8(link+510u,1u);
    w8(link+508u,2u);
    w8(link+532u,6u);
    w32(link+520u,link);
    w16(link+608u,384u);
    w32(link+540u,0x555555u);
    w32(link+536u,0x8e89bed6u);
    w32(link+528u,link+532u);
    w8(link+534u,accuracy);
    if(mode<5u&&((0x1au>>mode)&1u)!=0u)w16(link+610u,384u);
    uint32_t options=r8(link+99u);
    w32(link+640u,0u);
    w32(link+636u,(uint32_t)(uintptr_t)opencfw_em9305_child_320b3c);
    uint32_t random=options&1u;
    uint32_t type=random<<1;
    w8(link+664u,1u);
    uint32_t low,high;
    if(random==0u){
        high=r32(((uintptr_t)&em9305_ram_805af0 + 0x54u));
        low=r32(((uintptr_t)&em9305_ram_805af0 + 0x50u));
    }else{
        high=r32(((uintptr_t)&em9305_ram_805a6c + 0x24u));
        low=r32(((uintptr_t)&em9305_ram_805a6c + 0x20u));
    }
    uint32_t resolve=r8(((uintptr_t)&em9305_ram_805a6c + 0x31u));
    w32(link+616u,low);
    uint32_t flags=type+1u;
    w32(link+620u,high);
    w32(link+612u,flags);
    if(resolve!=0u){
        type|=0x51u;
        flags=type;
        w32(link+612u,type);
    }
    if(mode==0u){
        uint32_t value=((peer_type<<3)&8u)|flags|4u;
        w32(link+624u,peer_low);
        w32(link+628u,peer_high);
        w32(link+612u,value);
    }
    w32(link+644u,(uint32_t)(uintptr_t)opencfw_em9305_child_320d68);
    w8(link+241u,0u);
    w8(link+1u,0u);
    w8(link+656u,0x24u);
    w32(link+632u,link+112u);
    w8(link+2u,0u);
    return 0u;
}
