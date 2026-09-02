/* SPDX-License-Identifier: MIT */
/* Clean-room hardware register-profile restoration and mode finalization. */
typedef __UINT32_TYPE__ open_cfw_hw_restore_u32;
#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_register_power_toggle_42f1c8(void);
extern void open_cfw_bootloader_mode_finalize_41cde0(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_register_profile_restore_42f2fa(void)
{__asm volatile(
 "push {r7,lr}\nldr.w r0,[pc,#0x2f4]\nldr r0,[r0]\nubfx r0,r0,#4,#2\ncmp r0,#3\n"
 "beq mode_three\nldr.w r0,[pc,#0x2f4]\nldr.w r1,[pc,#0x2f4]\nldr r1,[r1]\n"
 "ldr r2,[r0]\nbfi r2,r1,#0,#6\nstr r2,[r0]\nldr r0,[pc,#0x2d8]\nldr r1,[pc,#0x2dc]\n"
 "ldr r1,[r1]\nldr r2,[r0]\nbfi r2,r1,#10,#4\nstr r2,[r0]\nb finalize\n"
 "mode_three: ldr r0,[pc,#0x2d8]\nldrb r0,[r0]\ncmp r0,#0\nbeq finalize\n"
 "movs r0,#0\nbl open_cfw_bootloader_register_power_toggle_42f1c8\n"
 "ldr r0,[pc,#0x2e4]\nldr r1,[pc,#0x2e4]\nldr r1,[r1]\nldr r2,[r0]\n"
 "bfi r2,r1,#29,#2\nstr r2,[r0]\nldr r0,[pc,#0x2d0]\nldr r1,[pc,#0x2cc]\n"
 "ldr r1,[r1]\nldr r2,[r0]\nbfi r2,r1,#0,#7\nstr r2,[r0]\n"
 "ldr r0,[pc,#0x2bc]\nldr r1,[r0]\nbics r1,r1,#0x100\nstr r1,[r0]\n"
 "ldr r0,[pc,#0x2ac]\nldr r1,[pc,#0x2a8]\nldr r1,[r1]\nldr r2,[r0]\n"
 "bfi r2,r1,#0,#7\nstr r2,[r0]\nldr r0,[pc,#0x288]\nldr r1,[pc,#0x2b4]\n"
 "ldr r1,[r1]\nldr r2,[r0]\nbfi r2,r1,#10,#4\nstr r2,[r0]\n"
 "movs r0,#1\nbl open_cfw_bootloader_register_power_toggle_42f1c8\n"
 "finalize: movs r1,#0\nmovs r0,#0\nbl open_cfw_bootloader_mode_finalize_41cde0\n"
 "movs r0,#0\npop {r1,pc}\n");}
#else
typedef struct {
 open_cfw_hw_restore_u32 mode_status,active;
 open_cfw_hw_restore_u32 register_a,saved_a,register_b,saved_b;
 open_cfw_hw_restore_u32 register_c,saved_c,register_d,saved_d;
 open_cfw_hw_restore_u32 register_e,saved_e;
 open_cfw_hw_restore_u32 power_toggles,finalize_calls;
} open_cfw_hw_restore_model;
static open_cfw_hw_restore_u32 open_cfw_hw_insert(open_cfw_hw_restore_u32 d,open_cfw_hw_restore_u32 s,open_cfw_hw_restore_u32 shift,open_cfw_hw_restore_u32 width){open_cfw_hw_restore_u32 mask=((1U<<width)-1U)<<shift;return(d&~mask)|((s<<shift)&mask);}
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_restore_u32 open_cfw_bootloader_hw_register_profile_restore_42f2fa_portable(open_cfw_hw_restore_model *s)
{
 if(s==0U)return 0U;
 if(((s->mode_status>>4U)&3U)!=3U){s->register_a=open_cfw_hw_insert(s->register_a,s->saved_a,0U,6U);s->register_b=open_cfw_hw_insert(s->register_b,s->saved_b,10U,4U);}
 else if(s->active!=0U){s->power_toggles++;s->register_c=open_cfw_hw_insert(s->register_c,s->saved_c,29U,2U);s->register_d=open_cfw_hw_insert(s->register_d,s->saved_d,0U,7U);s->register_e&=~0x100U;s->register_a=open_cfw_hw_insert(s->register_a,s->saved_a,0U,7U);s->register_b=open_cfw_hw_insert(s->register_b,s->saved_e,10U,4U);s->power_toggles++;}
 s->finalize_calls++;return 0U;
}
#endif
