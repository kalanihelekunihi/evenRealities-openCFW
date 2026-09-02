/* SPDX-License-Identifier: MIT */
/* Clean-room ring-descriptor selection and per-instance register publication. */
typedef __UINT32_TYPE__ open_cfw_hw_desc_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_descriptor_publish_42c45a(void)
{__asm volatile(
 "push {r4}\nldr r1, [r0, #4]\nldr.w r2, [r0, #0x850]\nadds r2, r2, #1\n"
 "ldr.w r3, [r0, #0x848]\nudiv r4, r2, r3\nmls r2, r3, r4, r2\n"
 "ldr.w r0, [r0, #0x854]\nlsls r2, r2, #5\nadd r0, r2\n"
 "ldr.w r2, [pc, #0x26c]\nldr r3, [r0]\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x128]\nldr r3, [r0, #4]\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x2c4]\nmovs r3, #0\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x218]\nldr r3, [r0, #8]\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x21c]\nldr r3, [r0, #0xc]\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x220]\nldr r3, [r0, #0x10]\nadds.w r4, r2, r1, lsl #12\n"
 "str.w r3, [r4, #0x218]\nldr r0, [r0, #0x14]\nadds.w r2, r2, r1, lsl #12\n"
 "str.w r0, [r2, #0x120]\npop {r4}\nbx lr\n");}
#else
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_desc_u32 open_cfw_bootloader_hw_descriptor_publish_42c45a_portable(
    open_cfw_hw_desc_u32 producer_index,open_cfw_hw_desc_u32 ring_size,
    const open_cfw_hw_desc_u32 *entries,open_cfw_hw_desc_u32 registers[6])
{open_cfw_hw_desc_u32 slot=(producer_index+1U)%ring_size;const open_cfw_hw_desc_u32 *entry=entries+slot*8U;registers[0]=entry[0];registers[1]=entry[1];registers[2]=entry[4];registers[3]=entry[2];registers[4]=entry[3];registers[5]=entry[5];return slot;}
#endif
