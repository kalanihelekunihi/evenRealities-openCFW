/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader four-instance initializer. */

typedef __UINT8_TYPE__ open_cfw_hw_u8;
typedef __UINT32_TYPE__ open_cfw_hw_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_instance_init_422ad4(void)
{
    __asm__ volatile(
        "push {r4, r5, r6}\n"
        "cmp r0, #4\n"
        "blo 1f\n"
        "movs r0, #5\n"
        "b 5f\n"
        "1:\n"
        "cmp r1, #0\n"
        "bne 2f\n"
        "movs r0, #6\n"
        "b 5f\n"
        "2:\n"
        "ldr r2, [r1]\n"
        "cmp r2, #0\n"
        "beq 3f\n"
        "ldr r2, [r1]\n"
        "ldr r2, [r2]\n"
        "bic r2, r2, #0xfe000000\n"
        "ldr.w r3, [pc, #0x8e8]\n"
        "cmp r2, r3\n"
        "bne 3f\n"
        "movs r0, #7\n"
        "b 5f\n"
        "3:\n"
        "mov.w r3, #0x11c\n"
        "ldr.w r4, [pc, #0x8dc]\n"
        "mul r2, r3, r0\n"
        "add r2, r4\n"
        "ldr r5, [r2]\n"
        "orrs r5, r5, #0x01000000\n"
        "str r5, [r2]\n"
        "mul r2, r3, r0\n"
        "add.w r5, r4, r2\n"
        "ldr r6, [r5]\n"
        "ands r6, r6, #0xff000000\n"
        "ldr.w r2, [pc, #0x908]\n"
        "orrs r6, r2\n"
        "str r6, [r5]\n"
        "mul r2, r3, r0\n"
        "add r2, r4\n"
        "str r0, [r2, #0x28]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb r2, [r5, #4]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "str r2, [r5, #0x30]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0x11a]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0x119]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0xdc]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0xdd]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "str.w r2, [r5, #0xd8]\n"
        "movs r2, #0\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "str.w r2, [r5, #0x9c]\n"
        "movs r2, #1\n"
        "mul r5, r3, r0\n"
        "add r5, r4\n"
        "strb.w r2, [r5, #0xde]\n"
        "muls r0, r3, r0\n"
        "add r0, r4\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "5:\n"
        "pop {r4, r5, r6}\n"
        "bx lr\n");
}
#else
typedef struct { open_cfw_hw_u8 bytes[0x11c]; } open_cfw_hw_instance;
extern open_cfw_hw_instance open_cfw_hw_host_instances[4];
static open_cfw_hw_u32 open_cfw_hw_read32(const open_cfw_hw_u8 *p)
{ return (open_cfw_hw_u32)p[0]|((open_cfw_hw_u32)p[1]<<8)|((open_cfw_hw_u32)p[2]<<16)|((open_cfw_hw_u32)p[3]<<24); }
static void open_cfw_hw_write32(open_cfw_hw_u8 *p,open_cfw_hw_u32 v)
{ p[0]=(open_cfw_hw_u8)v;p[1]=(open_cfw_hw_u8)(v>>8);p[2]=(open_cfw_hw_u8)(v>>16);p[3]=(open_cfw_hw_u8)(v>>24); }
open_cfw_hw_u32 open_cfw_bootloader_hw_instance_init_422ad4(open_cfw_hw_u32 index,open_cfw_hw_instance **out)
{
    open_cfw_hw_instance *instance; open_cfw_hw_u32 header;
    if(index>=4U)return 5U;if(out==(open_cfw_hw_instance**)0)return 6U;
    if(*out!=(open_cfw_hw_instance*)0 && (open_cfw_hw_read32((*out)->bytes)&~0xfe000000U)==0x01ea9e06U)return 7U;
    instance=&open_cfw_hw_host_instances[index];header=open_cfw_hw_read32(instance->bytes)|0x01000000U;
    open_cfw_hw_write32(instance->bytes,(header&0xff000000U)|0x00ea9e06U);
    open_cfw_hw_write32(instance->bytes+0x28,index);instance->bytes[4]=0;open_cfw_hw_write32(instance->bytes+0x30,0);
    instance->bytes[0x11a]=0;instance->bytes[0x119]=0;instance->bytes[0xdc]=0;instance->bytes[0xdd]=0;
    open_cfw_hw_write32(instance->bytes+0xd8,0);open_cfw_hw_write32(instance->bytes+0x9c,0);instance->bytes[0xde]=1;*out=instance;return 0;
}
#endif
