/* SPDX-License-Identifier: MIT
 * Complete task control flow reconstructed from 42de58..42e104.
 * Logging is an explicit unresolved provider, retaining severity/line only.
 * Runtime-enable/error transaction and queue implementation are dependencies.
 */
#include "../dfu_task/task.h"
extern void opencfw_dfu_log_detail_native(uint32_t,uint32_t,uint32_t);
#include "../update_core/update_core.h"
#include <string.h>
#define IMAGE ((opencfw_boot_image_header *)(uintptr_t)0x20026ef8u)
#define HANDLE ((uint32_t *)(uintptr_t)0x20027174u)
#define QUEUE (*(uint32_t volatile *)(uintptr_t)0x200004d8u)
#define PATH 0x004336e4u
static uint32_t stack_word(void) {
    return *(volatile uint32_t *)(uintptr_t)IMAGE->destination;
}
static void try_boot(uint32_t first_line,uint32_t second_line) {
    /* Stock checks only stack word bit29; no extra vector/range guard added. */
    if(stack_word()&(1u<<29)) {
        opencfw_boot_dfu_log(4,first_line);
        opencfw_boot_dfu_log(4,second_line);
        opencfw_boot_dfu_runtime_enable();
        opencfw_boot_vector_handoff(IMAGE->destination);
    }
}
void opencfw_boot_dfu_task(void) {
    opencfw_boot_dfu_message message;
    memset(&message,0,sizeof(message));
    for(;;) {
        if(opencfw_boot_dfu_queue_get(QUEUE,&message,0,0))return;
        if(message.command!=1u) {
            if(message.command==IMAGE->destination) {
                IMAGE->destination=OPENCFW_BOOT_APPLICATION_BASE;
                try_boot(0x237u,0x238u);
            }
            continue;
        }
        opencfw_boot_dfu_log(4,0x20bu);
        *HANDLE=opencfw_boot_file_open(PATH,opencfw_boot_stream_mode(1));
        if(!*HANDLE) {
            opencfw_boot_dfu_log(1,0x20eu);
            opencfw_boot_dfu_error_transaction();
        } else {
            uint32_t got=opencfw_boot_file_read(IMAGE,1,32,*HANDLE);
            if(*HANDLE) {opencfw_boot_file_close(*HANDLE);*HANDLE=0;}
            if(got!=32u) {
                opencfw_dfu_log_detail_native(1,0x214u,got);
                opencfw_boot_dfu_error_transaction();
                continue;
            }
            for(uint32_t line=0x21au;line<=0x21eu;line++)
                opencfw_boot_dfu_log(4,line);
            if(IMAGE->encoded_size&OPENCFW_BOOT_IMAGE_INSTALL_FLAG) {
                if(!(opencfw_boot_verify(HANDLE,IMAGE)&255u))
                    opencfw_boot_dfu_error_transaction();
                else opencfw_boot_program(HANDLE,IMAGE);
            }
        }
        if(IMAGE->destination!=OPENCFW_BOOT_APPLICATION_BASE) {
            opencfw_boot_dfu_log(1,0x229u);
            IMAGE->destination=OPENCFW_BOOT_APPLICATION_BASE;
        }
        try_boot(0x22eu,0x22fu);
    }
}
