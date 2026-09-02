/* SPDX-License-Identifier: MIT */
/* Clean-room stored-entry hardware-state reader and packed-field composer. */
typedef __UINT32_TYPE__ open_cfw_hw_compose_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_config_read_421548(void);
extern void open_cfw_bootloader_hw_state_commit_41cc04(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_hw_compose_u32 open_cfw_bootloader_hw_state_compose_42bdf0(void)
{
    __asm volatile(
        "push {r3,r4,r5,lr}\nsub sp,#0x10\nldr r0,[pc,#0x234]\nldr r0,[r0]\n"
        "ubfx r0,r0,#3,#1\ncmp r0,#0\nbeq gate_false\nldr r0,[pc,#0x1d4]\n"
        "ldr r0,[r0]\nubfx r0,r0,#0x1b,#1\nands r0,r0,#1\neors r0,r0,#1\n"
        "b gate_ready\ngate_false:\nmovs r0,#0\ngate_ready:\nuxtb r0,r0\n"
        "cmp r0,#0\nbeq read_primary\nmovs r0,#7\nb finish\n"
        "read_primary:\nldr r5,[pc,#0x1ac]\nadds r3,r5,#4\nmovs r2,#0x10\n"
        "mov.w r1,#0x25c\nmovs r0,#1\nbl open_cfw_bootloader_config_read_421548\n"
        "cmp r0,#0\nbne.w finish\nldr r0,[r5,#0x14]\nstr r0,[r5,#0x44]\n"
        "ldr r0,[r5,#0x18]\nstr r0,[r5,#0x48]\nldr r0,[r5,#0x1c]\n"
        "str r0,[r5,#0x4c]\nldr r0,[r5,#0x20]\nstr r0,[r5,#0x50]\n"
        "adds.w r0,r5,#0x44\nldr r1,[r5,#0x34]\nldr r2,[r0]\n"
        "bfi r2,r1,#0,#7\nstr r2,[r0]\nadds.w r0,r5,#0x48\n"
        "ldr r1,[r5,#0x38]\nldr r2,[r0]\nbfi r2,r1,#0,#7\nstr r2,[r0]\n"
        "adds.w r0,r5,#0x4c\nldr r1,[r5,#0x3c]\nldr r2,[r0]\n"
        "bfi r2,r1,#0,#7\nstr r2,[r0]\nadds.w r0,r5,#0x50\n"
        "ldr r1,[r5,#0x40]\nldr r2,[r0]\nbfi r2,r1,#0,#7\nstr r2,[r0]\n"
        "mov r3,sp\nmovs r2,#4\nmov.w r1,#0x270\nmovs r0,#1\n"
        "bl open_cfw_bootloader_config_read_421548\ncmp r0,#0\nbne finish\n"
        "ldr r0,[sp]\nstr r0,[r5,#0x54]\nldr r0,[sp,#4]\nstr r0,[r5,#0x58]\n"
        "ldr r0,[sp,#8]\nstr r0,[r5,#0x5c]\nldr r0,[sp,#0xc]\nstr r0,[r5,#0x60]\n"
        "mov r3,sp\nmovs r2,#1\nmov.w r1,#0x278\nmovs r0,#1\n"
        "bl open_cfw_bootloader_config_read_421548\nmovs r4,r0\ncmp r4,#0\nbeq compose\n"
        "movs r0,r4\nb finish\ncompose:\nldr r0,[sp]\nstr r0,[r5,#0x68]\n"
        "adds.w r1,r5,#0x24\nldr r0,[r5,#0x34]\nubfx r2,r0,#0x15,#7\n"
        "ldr r0,[r5,#0x38]\nubfx r0,r0,#0x15,#7\nadds r2,r0,r2\n"
        "movs r0,#2\nsdiv r0,r2,r0\nldr r2,[r1]\nbfi r2,r0,#0x15,#7\nstr r2,[r1]\n"
        "adds.w r0,r5,#0x28\nldr r2,[r5,#0x2c]\nlsrs r2,r2,#0x15\n"
        "ldr r3,[r0]\nbfi r3,r2,#0x15,#7\nstr r3,[r0]\n"
        "ldr r2,[r5,#0x34]\nlsrs r2,r2,#0x1c\nldr r3,[r1]\n"
        "bfi r3,r2,#0x1c,#1\nstr r3,[r1]\nldr r1,[r5,#0x2c]\n"
        "lsrs r1,r1,#0x1c\nldr r2,[r0]\nbfi r2,r1,#0x1c,#1\nstr r2,[r0]\n"
        "adds.w r0,r5,#0x34\nldr r1,[r5,#0x38]\nlsrs r1,r1,#0x15\n"
        "ldr r2,[r0]\nbfi r2,r1,#0x15,#7\nstr r2,[r0]\n"
        "ldr r1,[r5,#0x38]\nlsrs r1,r1,#0x1c\nldr r2,[r0]\n"
        "bfi r2,r1,#0x1c,#1\nstr r2,[r0]\nldr r1,[r5,#0x38]\n"
        "lsrs r1,r1,#0x11\nldr r2,[r0]\nbfi r2,r1,#0x11,#4\nstr r2,[r0]\n"
        "ldr r1,[r5,#0x38]\nlsrs r1,r1,#7\nldr r2,[r0]\n"
        "bfi r2,r1,#7,#0xa\nstr r2,[r0]\nmovs r0,#0x1f\n"
        "ldr r1,[r5,#0x68]\nbfi r1,r0,#0x14,#6\nstr r1,[r5,#0x68]\n"
        "ldr r0,[pc,#0x8c]\nstr r0,[r5]\nbl open_cfw_bootloader_hw_state_commit_41cc04\n"
        "movs r0,r4\nfinish:\nadd sp,#0x14\npop {r4,r5,pc}\n");
}
#else
typedef struct {
    open_cfw_hw_compose_u32 gate_control;
    open_cfw_hw_compose_u32 gate_status;
    open_cfw_hw_compose_u32 read_status[3];
    open_cfw_hw_compose_u32 primary[16];
    open_cfw_hw_compose_u32 secondary[4];
    open_cfw_hw_compose_u32 tertiary;
    open_cfw_hw_compose_u32 state[27];
    open_cfw_hw_compose_u32 commit_calls;
} open_cfw_hw_compose_model;
static open_cfw_hw_compose_u32 open_cfw_hw_compose_insert(open_cfw_hw_compose_u32 dst,open_cfw_hw_compose_u32 src,open_cfw_hw_compose_u32 shift,open_cfw_hw_compose_u32 width){open_cfw_hw_compose_u32 mask=((1U<<width)-1U)<<shift;return(dst&~mask)|((src<<shift)&mask);}
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_compose_u32 open_cfw_bootloader_hw_state_compose_42bdf0_portable(open_cfw_hw_compose_model *m)
{
    open_cfw_hw_compose_u32 i,a,b;
    if(m==0U)return ~0U;
    if(((m->gate_control>>3U)&1U)!=0U&&((m->gate_status>>27U)&1U)==0U)return 7U;
    if(m->read_status[0]!=0U)return m->read_status[0];
    for(i=0U;i<16U;i++)m->state[1U+i]=m->primary[i];
    for(i=0U;i<4U;i++)m->state[17U+i]=open_cfw_hw_compose_insert(m->state[5U+i],m->state[13U+i],0U,7U);
    if(m->read_status[1]!=0U)return m->read_status[1];for(i=0U;i<4U;i++)m->state[21U+i]=m->secondary[i];
    if(m->read_status[2]!=0U)return m->read_status[2];m->state[26]=m->tertiary;
    a=(m->state[13]>>21U)&127U;b=(m->state[14]>>21U)&127U;m->state[9]=open_cfw_hw_compose_insert(m->state[9],(a+b)/2U,21U,7U);
    m->state[10]=open_cfw_hw_compose_insert(m->state[10],m->state[11]>>21U,21U,7U);m->state[9]=open_cfw_hw_compose_insert(m->state[9],m->state[13]>>28U,28U,1U);m->state[10]=open_cfw_hw_compose_insert(m->state[10],m->state[11]>>28U,28U,1U);
    m->state[13]=open_cfw_hw_compose_insert(m->state[13],m->state[14]>>21U,21U,7U);m->state[13]=open_cfw_hw_compose_insert(m->state[13],m->state[14]>>28U,28U,1U);m->state[13]=open_cfw_hw_compose_insert(m->state[13],m->state[14]>>17U,17U,4U);m->state[13]=open_cfw_hw_compose_insert(m->state[13],m->state[14]>>7U,7U,10U);m->state[26]=open_cfw_hw_compose_insert(m->state[26],31U,20U,6U);m->state[0]=0x1f01600dU;m->commit_calls++;return 0U;
}
#endif
