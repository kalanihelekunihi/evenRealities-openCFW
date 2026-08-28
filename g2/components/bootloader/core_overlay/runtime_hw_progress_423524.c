/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 primary/secondary transfer progress. */

typedef __UINT8_TYPE__ open_cfw_hwp_u8;
typedef __UINT32_TYPE__ open_cfw_hwp_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_retained_descriptor_consume_427602(void);
extern void open_cfw_bootloader_retained_descriptor_read_427660(void);
extern void open_cfw_bootloader_hw_fifo_write_42330e(void);
extern void open_cfw_bootloader_hw_fifo_read_4232c8(void);
extern void open_cfw_bootloader_hw_fifo_pump_423390(void);
extern void open_cfw_bootloader_hw_fifo_snapshot_423350(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_primary_progress_423524(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r5, r4\n"
        "ldrb.w r0, [r5, #0x119]\n"
        "cmp r0, #0\n"
        "beq 8f\n"
        "movs r6, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r0, [r5, #0xd8]\n"
        "ldr.w r2, [r5, #0xa4]\n"
        "subs r2, r2, r0\n"
        "ldr.w r1, [r5, #0xa0]\n"
        "add r1, r0\n"
        "ldrb.w r0, [r5, #0xdc]\n"
        "cmp r0, #0\n"
        "beq 4f\n"
        "ldr r3, [r5, #0x40]\n"
        "ldr r0, [r5, #0x3c]\n"
        "subs r3, r3, r0\n"
        "cmp r2, r3\n"
        "bhs 1f\n"
        "str r2, [sp]\n"
        "b 2f\n"
        "1:\n"
        "str r3, [sp]\n"
        "2:\n"
        "ldr r2, [sp]\n"
        "adds.w r0, r5, #0x34\n"
        "bl open_cfw_bootloader_retained_descriptor_consume_427602\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne 5f\n"
        "movs r0, #0\n"
        "strb.w r0, [r5, #0x119]\n"
        "ldr.w r0, [r5, #0xb0]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr.w r1, [r5, #0xb4]\n"
        "movs r0, #1\n"
        "ldr.w r2, [r5, #0xb0]\n"
        "blx r2\n"
        "movs r6, #1\n"
        "b 5f\n"
        "4:\n"
        "mov r3, sp\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_fifo_write_42330e\n"
        "5:\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "ldr.w r1, [r5, #0xd8]\n"
        "ldr r0, [sp]\n"
        "adds r1, r0, r1\n"
        "str.w r1, [r5, #0xd8]\n"
        "6:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        "bne 9f\n"
        "ldr.w r0, [r5, #0xa8]\n"
        "cmp r0, #0\n"
        "beq 7f\n"
        "ldr.w r0, [r5, #0xd8]\n"
        "ldr.w r1, [r5, #0xa8]\n"
        "str r0, [r1]\n"
        "7:\n"
        "ldr.w r0, [r5, #0xd8]\n"
        "ldr.w r1, [r5, #0xa4]\n"
        "cmp r0, r1\n"
        "bne 8f\n"
        "ldrb.w r0, [r5, #0x119]\n"
        "cmp r0, #0\n"
        "beq 8f\n"
        "movs r0, #0\n"
        "strb.w r0, [r5, #0x119]\n"
        "ldr.w r0, [r5, #0xb0]\n"
        "cmp r0, #0\n"
        "beq 8f\n"
        "ldr.w r1, [r5, #0xb4]\n"
        "movs r0, #0\n"
        "ldr.w r2, [r5, #0xb0]\n"
        "blx r2\n"
        "8:\n"
        "ldrb.w r0, [r5, #0xdc]\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_fifo_pump_423390\n"
        "9:\n"
        "pop {r0, r1, r4, r5, r6, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_secondary_progress_423608(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r5, r0\n"
        "movs r4, r5\n"
        "ldrb.w r0, [r4, #0xdd]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_fifo_snapshot_423350\n"
        "1:\n"
        "ldrb.w r0, [r4, #0x11a]\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "movs r6, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r0, [r4, #0x9c]\n"
        "ldr r2, [r4, #0x68]\n"
        "subs r2, r2, r0\n"
        "ldr r1, [r4, #0x64]\n"
        "add r1, r0\n"
        "movs r0, #0\n"
        "str r0, [sp]\n"
        "ldrb.w r0, [r4, #0xdd]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr r0, [r4, #0x54]\n"
        "cmp r2, r0\n"
        "bhs 2f\n"
        "str r2, [sp]\n"
        "b 3f\n"
        "2:\n"
        "str r0, [sp]\n"
        "3:\n"
        "ldr r2, [sp]\n"
        "adds.w r0, r4, #0x4c\n"
        "bl open_cfw_bootloader_retained_descriptor_read_427660\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne 6f\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0x11a]\n"
        "ldr r0, [r4, #0x74]\n"
        "cmp r0, #0\n"
        "beq 6f\n"
        "ldr r1, [r4, #0x78]\n"
        "movs r0, #1\n"
        "ldr r2, [r4, #0x74]\n"
        "blx r2\n"
        "movs r6, #1\n"
        "b 6f\n"
        "5:\n"
        "mov r3, sp\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_fifo_read_4232c8\n"
        "6:\n"
        "movs r0, r6\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne 7f\n"
        "ldr.w r1, [r4, #0x9c]\n"
        "ldr r0, [sp]\n"
        "adds r1, r0, r1\n"
        "str.w r1, [r4, #0x9c]\n"
        "7:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        "bne 9f\n"
        "ldr r0, [r4, #0x6c]\n"
        "cmp r0, #0\n"
        "beq 8f\n"
        "ldr.w r0, [r4, #0x9c]\n"
        "ldr r1, [r4, #0x6c]\n"
        "str r0, [r1]\n"
        "8:\n"
        "ldr.w r0, [r4, #0x9c]\n"
        "ldr r1, [r4, #0x68]\n"
        "cmp r0, r1\n"
        "bne 9f\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0x11a]\n"
        "ldr r0, [r4, #0x74]\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "ldr r1, [r4, #0x78]\n"
        "movs r0, #0\n"
        "ldr r2, [r4, #0x74]\n"
        "blx r2\n"
        "9:\n"
        "pop {r0, r1, r4, r5, r6, pc}\n");
}
#else
typedef struct open_cfw_hwp_instance { open_cfw_hwp_u8 bytes[0x11c]; } open_cfw_hwp_instance;
extern open_cfw_hwp_u32 open_cfw_hwp_host_critical_enter(void);
extern void open_cfw_hwp_host_critical_restore(open_cfw_hwp_u32);
extern open_cfw_hwp_u32 open_cfw_hwp_host_primary_transfer(open_cfw_hwp_instance *, open_cfw_hwp_u32, open_cfw_hwp_u32 *);
extern open_cfw_hwp_u32 open_cfw_hwp_host_secondary_transfer(open_cfw_hwp_instance *, open_cfw_hwp_u32, open_cfw_hwp_u32 *);
extern void open_cfw_hwp_host_primary_callback(open_cfw_hwp_u32);
extern void open_cfw_hwp_host_secondary_callback(open_cfw_hwp_u32);
extern void open_cfw_hwp_host_pump(open_cfw_hwp_instance *);
extern void open_cfw_hwp_host_snapshot(open_cfw_hwp_instance *);
static open_cfw_hwp_u32 hwp_r32(const open_cfw_hwp_u8 *p) { return (open_cfw_hwp_u32)p[0]|((open_cfw_hwp_u32)p[1]<<8)|((open_cfw_hwp_u32)p[2]<<16)|((open_cfw_hwp_u32)p[3]<<24); }
static void hwp_w32(open_cfw_hwp_u8 *p, open_cfw_hwp_u32 v) { p[0]=(open_cfw_hwp_u8)v;p[1]=(open_cfw_hwp_u8)(v>>8);p[2]=(open_cfw_hwp_u8)(v>>16);p[3]=(open_cfw_hwp_u8)(v>>24); }
void open_cfw_bootloader_hw_primary_progress_423524(open_cfw_hwp_instance *i) {
 open_cfw_hwp_u32 aborted=0,count=0;
 if(i->bytes[0x119]){open_cfw_hwp_u32 t=open_cfw_hwp_host_critical_enter(),p=hwp_r32(i->bytes+0xd8),end=hwp_r32(i->bytes+0xa4),n=end-p;
  if(open_cfw_hwp_host_primary_transfer(i,n,&count)==0 && i->bytes[0xdc]){i->bytes[0x119]=0;if(hwp_r32(i->bytes+0xb0)){open_cfw_hwp_host_primary_callback(1);aborted=1;}}
  if(!aborted){p+=count;hwp_w32(i->bytes+0xd8,p);} open_cfw_hwp_host_critical_restore(t);
  if(!aborted){if(hwp_r32(i->bytes+0xa8))hwp_w32(i->bytes+0xac,p);if(p==end&&i->bytes[0x119]){i->bytes[0x119]=0;if(hwp_r32(i->bytes+0xb0))open_cfw_hwp_host_primary_callback(0);}}}
 if(i->bytes[0xdc]&&!aborted)open_cfw_hwp_host_pump(i);
}
void open_cfw_bootloader_hw_secondary_progress_423608(open_cfw_hwp_instance *i) {
 open_cfw_hwp_u32 aborted=0,count=0;if(i->bytes[0xdd])open_cfw_hwp_host_snapshot(i);if(!i->bytes[0x11a])return;
 open_cfw_hwp_u32 t=open_cfw_hwp_host_critical_enter(),p=hwp_r32(i->bytes+0x9c),end=hwp_r32(i->bytes+0x68),n=end-p;
 if(open_cfw_hwp_host_secondary_transfer(i,n,&count)==0&&i->bytes[0xdd]){i->bytes[0x11a]=0;if(hwp_r32(i->bytes+0x74)){open_cfw_hwp_host_secondary_callback(1);aborted=1;}}
 if(!aborted){p+=count;hwp_w32(i->bytes+0x9c,p);}open_cfw_hwp_host_critical_restore(t);
 if(!aborted){if(hwp_r32(i->bytes+0x6c))hwp_w32(i->bytes+0x70,p);if(p==end){i->bytes[0x11a]=0;if(hwp_r32(i->bytes+0x74))open_cfw_hwp_host_secondary_callback(0);}}
}
#endif
