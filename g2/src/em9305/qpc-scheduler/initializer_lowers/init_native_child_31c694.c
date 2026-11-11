#include <stdint.h>

/* Native 0x31c694..0x31c78a: initialise a connection record's link-layer
 * state: clear 216 bytes at +484, install the default procedure handlers,
 * the CRC init (0x555555) and access address (0x8e89bed6), PHY defaults
 * (+508/+510/+532/+534 and the 0x80 octet limits), the local or random
 * address pair (0x805a8c / 0x805b40 by flag bit 0 of +0xd) with its
 * address-type flags, the master SKD pointer for role 1 (+0xc) and clear
 * the state bytes. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern void opencfw_em9305_child_31c78c(void);
extern void opencfw_em9305_child_31ef5c(void);
extern void opencfw_em9305_child_31ed34(void);
extern void opencfw_em9305_child_31f298(void);
extern void opencfw_em9305_child_31f180(void);
extern void opencfw_em9305_child_31f400(void);

static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}

uint32_t opencfw_em9305_child_31c694(uintptr_t record)
{
    (void)opencfw_em9305_memset((void *)(record+484u),0u,0xd8u);
    uint32_t options=r8(record+0xeu);
    uint32_t handler=(uint32_t)(uintptr_t)opencfw_em9305_child_31c78c;
    w32(record+516u,handler);
    w32(record+512u,handler);
    uint32_t octets=r8(0x805a9cu);
    w8(record+510u,1u);
    w8(record+508u,2u);
    w8(record+532u,6u);
    w32(record+520u,(uint32_t)record);
    w16(record+608u,0x80u);
    w32(record+540u,0x555555u);
    w32(record+536u,0x8e89bed6u);
    w32(record+528u,(uint32_t)record+532u);
    w8(record+534u,octets);
    if(options&1u) w16(record+610u,0x80u);
    uint32_t local=r8(record+0xdu);
    w32(record+640u,(uint32_t)(uintptr_t)opencfw_em9305_child_31ef5c);
    uint32_t flags=(options<<4)&0x20u;
    w32(record+636u,(uint32_t)(uintptr_t)opencfw_em9305_child_31ed34);
    w8(record+664u,0u);
    uint32_t low,high;
    if(local&1u) {
        high=r32(0x805a90u);
        low=r32(0x805a8cu);
        flags|=2u;
    } else {
        high=r32(0x805b44u);
        low=r32(0x805b40u);
    }
    uint32_t privacy=r8(0x805a9du);
    w32(record+616u,low);
    w32(record+620u,high);
    w32(record+612u,flags|1u);
    if(privacy!=0u) w32(record+612u,flags|81u);
    uint32_t key=0u;
    if(r8(record+0xcu)==1u) {
        key=(uint32_t)record+112u;
        w8(record+656u,14u);
    }
    w32(record+652u,(uint32_t)(uintptr_t)opencfw_em9305_child_31f298);
    w32(record+648u,(uint32_t)(uintptr_t)opencfw_em9305_child_31f180);
    w32(record+644u,(uint32_t)(uintptr_t)opencfw_em9305_child_31f400);
    w32(record+632u,key);
    w8(record+241u,0u);
    w8(record+1u,0u);
    w8(record+2u,0u);
    return 0u;
}
