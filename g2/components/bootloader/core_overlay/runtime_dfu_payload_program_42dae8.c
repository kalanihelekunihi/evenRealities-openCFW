/* SPDX-License-Identifier: MIT */
/* Clean-room chunked DFU payload programmer and verifier. */
typedef __UINT32_TYPE__ open_cfw_dfu_program_u32;
#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_chunked_indirect_visit_42d9f0(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_stream_mode_42d84c(void);
extern void open_cfw_bootloader_file_open_4153a4(void);
extern void open_cfw_bootloader_file_prepare_4154d2(void);
extern void open_cfw_bootloader_file_read_415484(void);
extern void open_cfw_bootloader_chunked_source_compare_42da1e(void);
extern void open_cfw_bootloader_file_close_415446(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_dfu_payload_program_42dae8(void)
{
 __asm volatile(
 "push.w {r0,r1,r4,r5,r6,r7,r8,r9,r10,r11,lr}\nsub sp,#0x14\nldr r0,[sp,#0x18]\n"
 "ldr r4,[r0]\nbic r4,r4,#0xff000000\nsubs r4,#0x20\nldr r0,[sp,#0x18]\n"
 "ldr r5,[r0,#0x14]\nmovs r1,r4\nmovs r0,r5\nbl open_cfw_bootloader_chunked_indirect_visit_42d9f0\n"
 "ldr.w r6,[pc,#0x610]\nldr.w r7,[pc,#0x608]\nldr.w r8,[pc,#0x630]\n"
 "str r5,[sp,#0xc]\nstr r4,[sp,#8]\nldr.w r0,[pc,#0x62c]\nstr r0,[sp,#4]\n"
 "mov.w r0,#0x120\nstr r0,[sp]\nmov r3,r8\nmovs r2,r7\nmovs r1,r6\n"
 "movs r0,#4\nbl open_cfw_bootloader_log_4176ce\nmovs r0,#1\n"
 "bl open_cfw_bootloader_stream_mode_42d84c\nldr.w r9,[pc,#0x5d4]\nmovs r1,r0\n"
 "mov r0,r9\nbl open_cfw_bootloader_file_open_4153a4\nldr r1,[sp,#0x14]\nstr r0,[r1]\n"
 "ldr r0,[sp,#0x14]\nldr r0,[r0]\ncmp r0,#0\nbne opened\nstr.w r9,[sp,#8]\n"
 "ldr.w r0,[pc,#0x5bc]\nstr r0,[sp,#4]\nmovw r0,#0x123\nstr r0,[sp]\n"
 "mov r3,r8\nmovs r2,r7\nmovs r1,r6\nmovs r0,#1\nbl open_cfw_bootloader_log_4176ce\n"
 "b finish\nopened:\nmovs r2,#0\nmovs r1,#0x20\nldr r0,[sp,#0x14]\n"
 "ldr r0,[r0]\nbl open_cfw_bootloader_file_prepare_4154d2\nldr.w r0,[pc,#0x5d0]\n"
 "str r0,[sp,#4]\nmov.w r0,#0x128\nstr r0,[sp]\nmov r3,r8\nmovs r2,r7\n"
 "movs r1,r6\nmovs r0,#4\nbl open_cfw_bootloader_log_4176ce\nb loop_test\n"
 "use_remainder:\nmov r10,r4\nb read_chunk\nloop_body:\nmovs r0,#0x64\n"
 "mul r0,r0,r4\nldr r1,[sp,#0x18]\nldr r1,[r1]\nbic r1,r1,#0xff000000\n"
 "udiv r0,r0,r1\nrsbs.w r0,r0,#0x64\nstr r0,[sp,#0xc]\nstr r4,[sp,#8]\n"
 "ldr.w r0,[pc,#0x59c]\nstr r0,[sp,#4]\nmov.w r0,#0x12c\nstr r0,[sp]\n"
 "mov r3,r8\nmovs r2,r7\nmovs r1,r6\nmovs r0,#4\nbl open_cfw_bootloader_log_4176ce\n"
 "ldr.w r9,[pc,#0x55c]\nldr.w r0,[r9]\nldr r0,[r0,#4]\ncmp r0,r4\n"
 "bhs use_remainder\nldr.w r0,[r9]\nldr.w r10,[r0,#4]\nread_chunk:\n"
 "ldr.w r11,[pc,#0x574]\nldr r0,[sp,#0x14]\nldr r3,[r0]\nmov r2,r10\n"
 "movs r1,#1\nmov r0,r11\nbl open_cfw_bootloader_file_read_415484\n"
 "cmp r0,r10\nbeq program_chunk\nstr.w r10,[sp,#0xc]\nstr r0,[sp,#8]\n"
 "ldr.w r0,[pc,#0x530]\nstr r0,[sp,#4]\nmovw r0,#0x131\nstr r0,[sp]\n"
 "mov r3,r8\nmovs r2,r7\nmovs r1,r6\nmovs r0,#1\nbl open_cfw_bootloader_log_4176ce\n"
 "program_chunk:\nldr.w r0,[r9]\nldr r2,[r0,#4]\nmov r1,r11\nmovs r0,r5\n"
 "ldr.w r3,[r9]\nldr r3,[r3,#0x1c]\nblx r3\nldr.w r3,[r9]\n"
 "mov r2,r10\nmov r1,r11\nmovs r0,r5\nbl open_cfw_bootloader_chunked_source_compare_42da1e\n"
 "cmp r0,#0\nbeq advance\nstr.w r10,[sp,#0xc]\nstr r5,[sp,#8]\n"
 "ldr.w r0,[pc,#0x500]\nstr r0,[sp,#4]\nmov.w r0,#0x136\nstr r0,[sp]\n"
 "mov r3,r8\nmovs r2,r7\nmovs r1,r6\nmovs r0,#1\nbl open_cfw_bootloader_log_4176ce\n"
 "advance:\nsubs.w r4,r4,r10\nadds.w r5,r10,r5\nloop_test:\ncmp r4,#0\nbne loop_body\n"
 "ldr r0,[sp,#0x14]\nldr r0,[r0]\ncmp r0,#0\nbeq closed\nldr r0,[sp,#0x14]\n"
 "ldr r0,[r0]\nbl open_cfw_bootloader_file_close_415446\nmovs r0,#0\nldr r1,[sp,#0x14]\n"
 "str r0,[r1]\nclosed:\nldr.w r0,[pc,#0x4e0]\nstr r0,[sp,#4]\n"
 "mov.w r0,#0x13c\nstr r0,[sp]\nmov r3,r8\nmovs r2,r7\nmovs r1,r6\n"
 "movs r0,#4\nbl open_cfw_bootloader_log_4176ce\nfinish:\nadd sp,#0x1c\n"
 "pop.w {r4,r5,r6,r7,r8,r9,r10,r11,pc}\n");
}
#else
typedef struct {open_cfw_dfu_program_u32 encoded_size,start_address,chunk_size,open_result;const open_cfw_dfu_program_u32 *read_results,*compare_results;open_cfw_dfu_program_u32 result_count,read_calls,program_calls,compare_calls,short_read_logs,compare_error_logs,close_calls,handle,final_address;} open_cfw_dfu_program_model;
__attribute__((used,noinline,visibility("default")))
open_cfw_dfu_program_u32 open_cfw_bootloader_dfu_payload_program_42dae8_portable(open_cfw_dfu_program_model *m)
{open_cfw_dfu_program_u32 remain,n,i=0;if(m==0U||m->chunk_size==0U)return~0U;remain=(m->encoded_size&0x00ffffffU)-32U;m->handle=m->open_result;if(m->handle==0U)return 1U;m->final_address=m->start_address;while(remain!=0U){if(i>=m->result_count)return 2U;n=remain<m->chunk_size?remain:m->chunk_size;m->read_calls++;if(m->read_results[i]!=n)m->short_read_logs++;m->program_calls++;m->compare_calls++;if(m->compare_results[i]!=0U)m->compare_error_logs++;remain-=n;m->final_address+=n;i++;}m->close_calls++;m->handle=0U;return 0U;}
#endif
