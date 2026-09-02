/* SPDX-License-Identifier: MIT */
/* Clean-room DFU image open/read/CRC/close verifier. */
typedef __UINT8_TYPE__ open_cfw_dfu_crc_u8;
typedef __UINT32_TYPE__ open_cfw_dfu_crc_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_stream_mode_42d84c(void);
extern void open_cfw_bootloader_file_open_4153a4(void);
extern void open_cfw_bootloader_file_prepare_4154d2(void);
extern void open_cfw_bootloader_file_read_415484(void);
extern void open_cfw_bootloader_crc32_table_42e1ec(void);
extern void open_cfw_bootloader_file_close_415446(void);
extern void open_cfw_bootloader_log_4176ce(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_dfu_crc_u32 open_cfw_bootloader_dfu_image_crc_check_42d890(void)
{
    __asm volatile(
        "push.w {r4,r5,r6,r7,r8,r9,lr}\nsub sp,#0x14\nmovs r5,r0\nmovs r6,r1\n"
        "movs r0,#0\nstr r0,[sp,#0x10]\nldr r4,[r6]\nbic r4,r4,#0xff000000\n"
        "subs r4,#8\nmovs r0,#1\nbl open_cfw_bootloader_stream_mode_42d84c\n"
        "ldr.w r7,[pc,#0x858]\nmovs r1,r0\nmovs r0,r7\nbl open_cfw_bootloader_file_open_4153a4\n"
        "str r0,[r5]\nldr r0,[r5]\ncmp r0,#0\nbne open_ok\nstr r7,[sp,#8]\n"
        "ldr.w r0,[pc,#0x848]\nstr r0,[sp,#4]\nmovs r0,#0xcf\nstr r0,[sp]\n"
        "ldr.w r3,[pc,#0x840]\nldr.w r2,[pc,#0x840]\nldr.w r1,[pc,#0x840]\n"
        "movs r0,#1\nbl open_cfw_bootloader_log_4176ce\nmovs r0,#0\nb finish\n"
        "open_ok:\nmovs r2,#0\nmovs r1,#8\nldr r0,[r5]\nbl open_cfw_bootloader_file_prepare_4154d2\n"
        "movs r7,#0\nb loop_test\nloop_body:\nldr.w r9,[pc,#0x828]\nldr r3,[r5]\n"
        "ldr.w r0,[r8]\nldr r2,[r0,#4]\nmovs r1,#1\nmov r0,r9\n"
        "bl open_cfw_bootloader_file_read_415484\nldr.w r1,[r8]\nldr r1,[r1,#4]\n"
        "cmp r0,r1\nbeq full_crc\nstr r0,[sp,#8]\nldr.w r0,[pc,#0x80c]\n"
        "str r0,[sp,#4]\nmovs r0,#0xd7\nstr r0,[sp]\nldr.w r3,[pc,#0x7f4]\n"
        "ldr.w r2,[pc,#0x7f4]\nldr.w r1,[pc,#0x7f4]\nmovs r0,#1\n"
        "bl open_cfw_bootloader_log_4176ce\nfull_crc:\nadd r2,sp,#0x10\nldr.w r0,[r8]\n"
        "ldr r1,[r0,#4]\nmov r0,r9\nbl open_cfw_bootloader_crc32_table_42e1ec\n"
        "str r0,[sp,#0x10]\nadds r7,r7,#1\nloop_test:\nldr.w r8,[pc,#0x7e4]\n"
        "ldr.w r0,[r8]\nldr r0,[r0,#4]\nudiv r0,r4,r0\ncmp r7,r0\nblo loop_body\n"
        "ldr.w r0,[r8]\nldr r0,[r0,#4]\nudiv r1,r4,r0\nmls r4,r0,r1,r4\n"
        "cmp r4,#0\nbeq close_file\nldr.w r7,[pc,#0x7b8]\nldr r3,[r5]\n"
        "movs r2,r4\nmovs r1,#1\nmovs r0,r7\nbl open_cfw_bootloader_file_read_415484\n"
        "cmp r0,r4\nbeq tail_crc\nstr r4,[sp,#0xc]\nstr r0,[sp,#8]\n"
        "ldr.w r0,[pc,#0x7ac]\nstr r0,[sp,#4]\nmovs r0,#0xdf\nstr r0,[sp]\n"
        "ldr.w r3,[pc,#0x788]\nldr.w r2,[pc,#0x788]\nldr.w r1,[pc,#0x788]\n"
        "movs r0,#1\nbl open_cfw_bootloader_log_4176ce\ntail_crc:\nadd r2,sp,#0x10\n"
        "movs r1,r4\nmovs r0,r7\nbl open_cfw_bootloader_crc32_table_42e1ec\n"
        "str r0,[sp,#0x10]\nclose_file:\nldr r0,[r5]\ncmp r0,#0\nbeq report\n"
        "ldr r0,[r5]\nbl open_cfw_bootloader_file_close_415446\nmovs r0,#0\nstr r0,[r5]\n"
        "report:\nldr.w r0,[pc,#0x778]\nldr r0,[r0,#4]\nstr r0,[sp,#0xc]\n"
        "ldr r0,[sp,#0x10]\nstr r0,[sp,#8]\nldr.w r0,[pc,#0x770]\nstr r0,[sp,#4]\n"
        "movs r0,#0xe4\nstr r0,[sp]\nldr.w r3,[pc,#0x744]\nldr.w r2,[pc,#0x744]\n"
        "ldr.w r1,[pc,#0x744]\nmovs r0,#4\nbl open_cfw_bootloader_log_4176ce\n"
        "ldr r0,[sp,#0x10]\nldr r1,[r6,#4]\ncmp r0,r1\nbne mismatch\nmovs r0,#1\nb result\n"
        "mismatch:\nmovs r0,#0\nresult:\nuxtb r0,r0\nfinish:\nadd sp,#0x14\n"
        "pop.w {r4,r5,r6,r7,r8,r9,pc}\n");
}
#else
typedef struct {
    open_cfw_dfu_crc_u32 encoded_size;
    open_cfw_dfu_crc_u32 expected_crc;
    open_cfw_dfu_crc_u32 chunk_size;
    open_cfw_dfu_crc_u32 open_result;
    const open_cfw_dfu_crc_u32 *read_results;
    const open_cfw_dfu_crc_u32 *crc_results;
    open_cfw_dfu_crc_u32 read_result_count;
    open_cfw_dfu_crc_u32 read_calls;
    open_cfw_dfu_crc_u32 short_read_logs;
    open_cfw_dfu_crc_u32 close_calls;
    open_cfw_dfu_crc_u32 handle;
    open_cfw_dfu_crc_u32 final_crc;
} open_cfw_dfu_crc_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_dfu_crc_u32 open_cfw_bootloader_dfu_image_crc_check_42d890_portable(
    open_cfw_dfu_crc_model *model)
{
    open_cfw_dfu_crc_u32 payload_size, full_chunks, remainder, reads, index;
    if (model == 0U || model->chunk_size == 0U) return 0U;
    model->handle = model->open_result;
    if (model->handle == 0U) return 0U;
    payload_size = (model->encoded_size & 0x00FFFFFFU) - 8U;
    full_chunks = payload_size / model->chunk_size;
    remainder = payload_size % model->chunk_size;
    reads = full_chunks + (remainder != 0U ? 1U : 0U);
    if (reads > model->read_result_count) return 0U;
    for (index = 0U; index < reads; index++) {
        open_cfw_dfu_crc_u32 expected_read = index < full_chunks ? model->chunk_size : remainder;
        model->read_calls++;
        if (model->read_results[index] != expected_read) model->short_read_logs++;
        /* A short read is logged but still included by the stock service. */
        model->final_crc = model->crc_results[index];
    }
    model->close_calls++;
    model->handle = 0U;
    return model->final_crc == model->expected_crc ? 1U : 0U;
}
#endif
