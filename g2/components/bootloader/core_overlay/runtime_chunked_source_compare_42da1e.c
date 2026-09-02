/* SPDX-License-Identifier: MIT */
/* Clean-room bounded 4 KiB source-reader and memory comparison service. */
typedef __UINT8_TYPE__ open_cfw_chunk_compare_u8;
typedef __UINT32_TYPE__ open_cfw_chunk_compare_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_compare_prepare_41e348(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_memory_compare_415758(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_chunked_source_compare_42da1e(void)
{__asm volatile(
 "push.w {r4,r5,r6,r7,r8,r9,r10,r11,lr}\nsub sp,#0x14\nmovs r6,r0\nmovs r7,r1\n"
 "mov r8,r2\nmov r9,r3\nmovs.w r10,#0\nmov r4,r8\nmovs r5,#0\n"
 "movs r1,#1\nmovs r0,#0\nbl open_cfw_bootloader_compare_prepare_41e348\nb loop_test\n"
 "success_log: str r4,[sp,#0x10]\nstr.w r8,[sp,#0xc]\nstr r6,[sp,#8]\n"
 "ldr.w r0,[pc,#0x6ec]\nstr r0,[sp,#4]\nmov.w r0,#0x10e\nstr r0,[sp]\n"
 "ldr.w r3,[pc,#0x6e4]\nldr.w r2,[pc,#0x6bc]\nldr.w r1,[pc,#0x6bc]\n"
 "movs r0,#4\nbl open_cfw_bootloader_log_4176ce\n"
 "adds.w r10,r11,r10\nsubs.w r4,r4,r11\n"
 "loop_test: cmp r4,#0\nbeq finish\nmovw r0,#0x1001\ncmp r4,r0\n"
 "blo short_chunk\nmov.w r11,#0x1000\nb chunk_ready\nshort_chunk: mov r11,r4\n"
 "chunk_ready: ldr.w r5,[pc,#0x698]\nmov r2,r11\nadds.w r1,r10,r6\nmovs r0,r5\n"
 "ldr.w r3,[r9,#0x18]\nblx r3\nmov r2,r11\nadds.w r1,r10,r7\nmovs r0,r5\n"
 "bl open_cfw_bootloader_memory_compare_415758\nmovs r5,r0\ncmp r5,#0\nbeq success_log\n"
 "str.w r8,[sp,#0xc]\nstr r6,[sp,#8]\nldr.w r0,[pc,#0x690]\nstr r0,[sp,#4]\n"
 "movw r0,#0x10b\nstr r0,[sp]\nldr.w r3,[pc,#0x680]\nldr.w r2,[pc,#0x658]\n"
 "ldr.w r1,[pc,#0x658]\nmovs r0,#1\nbl open_cfw_bootloader_log_4176ce\n"
 "finish: movs r0,r5\nadd sp,#0x14\npop.w {r4,r5,r6,r7,r8,r9,r10,r11,pc}\n");}
#else
typedef void (*open_cfw_chunk_reader)(open_cfw_chunk_compare_u8 *,const open_cfw_chunk_compare_u8 *,open_cfw_chunk_compare_u32);
typedef struct {open_cfw_chunk_reader read;open_cfw_chunk_compare_u32 chunks;open_cfw_chunk_compare_u32 compared;} open_cfw_chunk_compare_model;
__attribute__((used,noinline,visibility("default")))
int open_cfw_bootloader_chunked_source_compare_42da1e_portable(
    open_cfw_chunk_compare_model *state,const open_cfw_chunk_compare_u8 *source,
    const open_cfw_chunk_compare_u8 *expected,open_cfw_chunk_compare_u32 length)
{
    open_cfw_chunk_compare_u8 buffer[4096];open_cfw_chunk_compare_u32 offset=0U;
    if(state==0U||state->read==0U||source==0U||expected==0U)return -1;
    while(offset<length){open_cfw_chunk_compare_u32 chunk=length-offset>4096U?4096U:length-offset;open_cfw_chunk_compare_u32 i;state->read(buffer,source+offset,chunk);state->chunks++;for(i=0U;i<chunk;i++)if(buffer[i]!=expected[offset+i])return (int)buffer[i]-(int)expected[offset+i];offset+=chunk;state->compared=offset;}
    return 0;
}
#endif
