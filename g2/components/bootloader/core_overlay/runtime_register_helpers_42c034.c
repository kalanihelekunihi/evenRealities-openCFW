/* SPDX-License-Identifier: MIT */
/* Clean-room hardware-status, interrupt-register, and NVIC/SCB helpers. */
typedef __INT16_TYPE__ open_cfw_reg_i16;
typedef __UINT8_TYPE__ open_cfw_reg_u8;
typedef __UINT16_TYPE__ open_cfw_reg_u16;
typedef __UINT32_TYPE__ open_cfw_reg_u32;
#define OPEN_CFW_REG_HANDLE_MAGIC 0x01123456U

#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_status_route_42c034(
 open_cfw_reg_u32 instance, open_cfw_reg_u32 route)
{__asm volatile(
 "ldr.w r2, [pc, #1712]\nadds.w r3, r2, r0, lsl #12\nldr.w r3, [r3, #284]\n"
 "ubfx r3, r3, #1, #3\ncmp r3, r1\nbeq 1f\n"
 "adds.w r3, r2, r0, lsl #12\nldr.w r3, [r3, #284]\nubfx r3, r3, #5, #3\n"
 "cmp r3, r1\nbne 2f\nmovs r1, #16\nadds.w r2, r2, r0, lsl #12\n"
 "str.w r1, [r2, #284]\n3:\nmovs r0, #1\n4:\nbx lr\n"
 "1:\nmovs r1, #1\nadds.w r2, r2, r0, lsl #12\nstr.w r1, [r2, #284]\nb 3b\n"
 "2:\nmovs r0, #0\nb 4b\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_error_classify_42c076(
 open_cfw_reg_u32 instance, open_cfw_reg_u32 pending)
{__asm volatile(
 "movs r2, r0\nmovs r0, #0\nldr.w r3, [pc, #1644]\n"
 "adds.w r3, r3, r2, lsl #12\nldr.w r2, [r3, #516]\norrs r1, r2\n"
 "tst r1, #108\nbeq 1f\nmovs.w r0, #0x8000000\nb 4f\n"
 "1:\nlsls r2, r1, #22\nbpl 2f\nldr.w r0, [pc, #1616]\nb 4f\n"
 "2:\nlsls r2, r1, #27\nbpl 3f\nldr.w r0, [pc, #1612]\nb 4f\n"
 "3:\ntst r1, #0x4800\nbeq 4f\nmovs r0, #1\n4:\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_enable_42c63a(
 open_cfw_reg_u32 *handle, open_cfw_reg_u32 mask)
{__asm volatile(
 "cmp r0, #0\nbeq 1f\nldr r2, [r0]\nbic r2, r2, #0xfe000000\n"
 "ldr.w r3, [pc, #1896]\ncmp r2, r3\nbeq 2f\n1:\nmovs r0, #2\nb 4f\n"
 "2:\nlsls r2, r1, #30\nbpl 3f\nmovs r0, #6\nb 4f\n"
 "3:\nldr r0, [r0, #4]\nldr r2, [pc, #140]\nadds.w r3, r2, r0, lsl #12\n"
 "ldr.w r3, [r3, #512]\norrs r1, r3\nadds.w r2, r2, r0, lsl #12\n"
 "str.w r1, [r2, #512]\nmovs r0, #0\n4:\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_status_get_42c672(
 open_cfw_reg_u32 *handle, open_cfw_reg_u32 enabled_only,
 open_cfw_reg_u32 *status)
{__asm volatile(
 "push {r4}\ncmp r0, #0\nbeq 1f\nldr r3, [r0]\nbic r3, r3, #0xfe000000\n"
 "ldr.w r4, [pc, #1840]\ncmp r3, r4\nbeq 2f\n1:\nmovs r0, #2\nb 5f\n"
 "2:\ncmp r2, #0\nbne 3f\nmovs r0, #6\nb 5f\n"
 "3:\nldr r0, [r0, #4]\nldr r4, [pc, #80]\nadds.w r3, r4, r0, lsl #12\n"
 "ldr.w r3, [r3, #516]\nuxtb r1, r1\ncmp r1, #0\nbeq 4f\n"
 "adds.w r4, r4, r0, lsl #12\nldr.w r0, [r4, #512]\nands r3, r0\n"
 "4:\nstr r3, [r2]\nmovs r0, #0\n5:\npop {r4}\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_clear_42c6b6(
 open_cfw_reg_u32 *handle, open_cfw_reg_u32 mask)
{__asm volatile(
 "cmp r0, #0\nbeq 1f\nldr r2, [r0]\nbic r2, r2, #0xfe000000\n"
 "ldr.w r3, [pc, #1772]\ncmp r2, r3\nbeq 2f\n1:\nmovs r0, #2\nb 3f\n"
 "2:\nldr r0, [r0, #4]\nldr r2, [pc, #24]\nadds.w r3, r2, r0, lsl #12\n"
 "str.w r1, [r3, #520]\nadds.w r2, r2, r0, lsl #12\nldr.w r0, [r2, #516]\n"
 "movs r0, #0\n3:\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_nvic_enable_bit_430240(open_cfw_reg_u32 interrupt)
{__asm volatile(
 "movs r1, r0\nsxth r1, r1\ncmp r1, #0\nbmi 1f\nmovs r2, #1\n"
 "ands r1, r0, #31\nlsls r2, r1\nldr r1, [pc, #512]\nsxth r0, r0\n"
 "lsrs r0, r0, #5\nstr.w r2, [r1, r0, lsl #2]\n1:\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_scb_priority_nibble_43025c(
 open_cfw_reg_u32 exception, open_cfw_reg_u32 priority)
{__asm volatile(
 "movs r2, r0\nsxth r2, r2\ncmp r2, #0\nbmi 1f\nlsls r1, r1, #4\n"
 "ldr r2, [pc, #496]\nsxth r0, r0\nstrb r1, [r2, r0]\nb 2f\n"
 "1:\nlsls r1, r1, #4\nldr r2, [pc, #488]\nsxth r0, r0\nands r0, r0, #15\n"
 "add r0, r2\nstrb r1, [r0, #-4]\n2:\nbx lr\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_nvic_enable_bit_430470(open_cfw_reg_u32 interrupt)
{__asm volatile(
 "movs r1, r0\nsxth r1, r1\ncmp r1, #0\nbmi 1f\nmovs r2, #1\n"
 "ands r1, r0, #31\nlsls r2, r1\nldr.w r1, [pc, #440]\nsxth r0, r0\n"
 "lsrs r0, r0, #5\nstr.w r2, [r1, r0, lsl #2]\n1:\nbx lr\n");}
#else
typedef struct open_cfw_reg_instance {open_cfw_reg_u32 control,status,clear;} open_cfw_reg_instance;
typedef struct open_cfw_reg_handle {open_cfw_reg_u32 word0,instance;} open_cfw_reg_handle;
__attribute__((used,noinline,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_status_route_42c034_portable(open_cfw_reg_u32 *route_register,open_cfw_reg_u32 route)
{open_cfw_reg_u32 value=*route_register;if(((value>>1)&7U)==route){*route_register=1U;return 1U;}if(((value>>5)&7U)==route){*route_register=16U;return 1U;}return 0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_error_classify_42c076_portable(open_cfw_reg_u32 status,open_cfw_reg_u32 pending)
{open_cfw_reg_u32 value=status|pending;if((value&0x6CU)!=0U)return 0x08000000U;if((value&(1U<<9))!=0U)return 0x08000001U;if((value&(1U<<4))!=0U)return 0x08000002U;if((value&0x4800U)!=0U)return 1U;return 0U;}
static open_cfw_reg_u32 open_cfw_reg_valid(const open_cfw_reg_handle *handle){return handle!=(const open_cfw_reg_handle *)0&&(handle->word0&~0xFE000000U)==OPEN_CFW_REG_HANDLE_MAGIC;}
__attribute__((used,noinline,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_enable_42c63a_portable(const open_cfw_reg_handle *handle,open_cfw_reg_u32 mask,open_cfw_reg_instance *instance)
{if(!open_cfw_reg_valid(handle))return 2U;if((mask&2U)!=0U)return 6U;instance->control|=mask;return 0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_status_get_42c672_portable(const open_cfw_reg_handle *handle,open_cfw_reg_u32 enabled_only,open_cfw_reg_u32 *status,const open_cfw_reg_instance *instance)
{if(!open_cfw_reg_valid(handle))return 2U;if(status==(open_cfw_reg_u32 *)0)return 6U;*status=(open_cfw_reg_u8)enabled_only?instance->status&instance->control:instance->status;return 0U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_reg_u32 open_cfw_bootloader_hw_interrupt_clear_42c6b6_portable(const open_cfw_reg_handle *handle,open_cfw_reg_u32 mask,open_cfw_reg_instance *instance)
{if(!open_cfw_reg_valid(handle))return 2U;instance->clear=mask;return 0U;}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_nvic_enable_bit_430240_portable(open_cfw_reg_i16 interrupt,open_cfw_reg_u32 *registers){if(interrupt>=0)registers[(open_cfw_reg_u16)interrupt>>5]=1U<<((open_cfw_reg_u16)interrupt&31U);}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_scb_priority_nibble_43025c_portable(open_cfw_reg_i16 exception,open_cfw_reg_u32 priority,open_cfw_reg_u8 *external,open_cfw_reg_u8 *system){if(exception>=0)external[(open_cfw_reg_u16)exception]=(open_cfw_reg_u8)(priority<<4);else system[((open_cfw_reg_u16)exception&15U)-4U]=(open_cfw_reg_u8)(priority<<4);}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_nvic_enable_bit_430470_portable(open_cfw_reg_i16 interrupt,open_cfw_reg_u32 *registers){if(interrupt>=0)registers[(open_cfw_reg_u16)interrupt>>5]=1U<<((open_cfw_reg_u16)interrupt&31U);}
#endif
