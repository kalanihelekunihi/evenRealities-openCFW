/* SPDX-License-Identifier: MIT */
/* Clean-room post-MSPI mode, vector, CRC32, and terminal primitives. */
typedef __UINT8_TYPE__ open_cfw_misc_u8;
typedef __UINT32_TYPE__ open_cfw_misc_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
const char *open_cfw_bootloader_stream_mode_42d84c(open_cfw_misc_u32 flags)
{
 __asm volatile(
  "tst r0, #3\nbeq 1f\nlsls r1, r0, #23\nbpl 2f\nlsls r0, r0, #21\nbpl 3f\n"
  "adr r0, #628\nb 9f\n3:\nadr r0, #628\nb 9f\n2:\nadr r0, #628\nb 9f\n"
  "1:\nlsls r1, r0, #30\nbpl 8f\nlsls r1, r0, #20\nbpl 4f\nadr r0, #620\nb 9f\n"
  "4:\nlsls r1, r0, #23\nbpl 7f\nlsls r0, r0, #21\nbpl 5f\nadr r0, #612\nb 9f\n"
  "5:\nadr r0, #604\nb 9f\n7:\nadr r0, #604\nb 9f\n8:\nadr r0, #604\n9:\nbx lr\n");
}

__attribute__((used,noinline,naked,visibility("default")))
void *open_cfw_bootloader_runtime_context_get_42d88a(void)
{ __asm volatile("ldr.w r0, [pc, #2168]\nbx lr\n"); }

__attribute__((used,noinline,naked,noreturn,visibility("default")))
void open_cfw_bootloader_vector_handoff_42dc90(const open_cfw_misc_u32 *vectors)
{
 __asm volatile("movw r1, #0xed08\nmovt r1, #0xe000\nstr r0, [r1]\n"
                "ldr.w sp, [r0]\nldr r1, [r0, #4]\nbx r1\n");
}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_misc_u32 open_cfw_bootloader_crc32_table_42e1ec(
 const open_cfw_misc_u8 *data, open_cfw_misc_u32 length,
 const open_cfw_misc_u32 *seed)
{
 __asm volatile(
  "push {r4, r5}\nmovs r3, r0\ncmp r2, #0\nbne 1f\nmovs.w r0, #-1\nb 2f\n"
  "1:\nldr r0, [r2]\nmvns r0, r0\n2:\nmovs r4, #0\nb 4f\n"
  "3:\nldr r2, [pc, #28]\nldrb r5, [r3, r4]\neors r5, r0\nand r5, r5, #255\n"
  "ldr.w r2, [r2, r5, lsl #2]\neors.w r0, r2, r0, lsr #8\nadds r4, r4, #1\n"
  "4:\ncmp r4, r1\nblo 3b\nmvns r0, r0\npop {r4, r5}\nbx lr\n");
}

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_misc_u32 open_cfw_bootloader_terminal_mode_42e514(open_cfw_misc_u32 mode)
{
 __asm volatile(
  "uxtb r0, r0\ncmp r0, #0\nbeq 1f\ncmp r0, #1\nbeq 2f\nb 3f\n"
  "1:\nmovs r0, #212\nldr r1, [pc, #16]\nstr r0, [r1]\n4:\nb 4b\n"
  "2:\nmovs r0, #27\nldr r1, [pc, #12]\nstr r0, [r1]\n5:\nb 5b\n"
  "3:\nmovs r0, #6\nbx lr\n");
}
#else
typedef struct open_cfw_misc_vector_state {
 open_cfw_misc_u32 vector_table, stack_pointer, reset_handler;
} open_cfw_misc_vector_state;

__attribute__((used,noinline,visibility("default")))
const char *open_cfw_bootloader_stream_mode_42d84c_portable(open_cfw_misc_u32 flags)
{
 if ((flags&3U)!=0U) {
  if ((flags&(1U<<8))!=0U) return (flags&(1U<<10))!=0U?"w+":"a+";
  return "r+";
 }
 if ((flags&(1U<<1))!=0U) {
  if ((flags&(1U<<11))!=0U) return "a";
  if ((flags&(1U<<8))!=0U) return (flags&(1U<<10))!=0U?"w":"a";
  return "w";
 }
 return "r";
}

__attribute__((used,noinline,visibility("default")))
void *open_cfw_bootloader_runtime_context_get_42d88a_portable(void *context)
{ return context; }

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_vector_handoff_42dc90_portable(
 const open_cfw_misc_u32 *vectors, open_cfw_misc_vector_state *state)
{ state->vector_table=(open_cfw_misc_u32)(unsigned long)vectors;
  state->stack_pointer=vectors[0];state->reset_handler=vectors[1]; }

__attribute__((used,noinline,visibility("default")))
open_cfw_misc_u32 open_cfw_bootloader_crc32_table_42e1ec_portable(
 const open_cfw_misc_u8 *data, open_cfw_misc_u32 length,
 const open_cfw_misc_u32 *seed)
{
 open_cfw_misc_u32 crc=~(seed!=(const open_cfw_misc_u32 *)0?*seed:0U);
 open_cfw_misc_u32 index,bit;
 for(index=0U;index<length;++index){crc^=data[index];for(bit=0U;bit<8U;++bit)
  crc=(crc>>1)^((crc&1U)!=0U?0xEDB88320U:0U);}
 return ~crc;
}

__attribute__((used,noinline,visibility("default")))
open_cfw_misc_u32 open_cfw_bootloader_terminal_mode_42e514_portable(
 open_cfw_misc_u32 mode, open_cfw_misc_u32 *control)
{ if((open_cfw_misc_u8)mode==0U){*control=212U;return 0U;}
  if((open_cfw_misc_u8)mode==1U){*control=27U;return 0U;}return 6U; }
#endif
