/* SPDX-License-Identifier: MIT */
/* Candidate reconstruction of the observed task descriptor writes.
 * Only touched words are described; this does not own the whole state area.
 * Header semantics are corroborated by the pinned gxDNN command model;
 * target execution and full state ownership remain unqualified. See
 * docs/research/gx8002-gxdnn-cmodel.md. */
#include <stdint.h>
/* gxDNN parse_base_cmd selects a base register by opcode minus 0x80.
 * parse_next_cmd uses bit 16 for an absolute link (bit 17 is clear).
 * cmd_process records the completed address and sends interrupt 1 when
 * header bit 22 is set. Opcode 0xff has no arithmetic operation; a
 * self-linked instance enters the model's idle handling. */
enum {
    SNPU_COMMAND_BASE_SLOT_0 = 0x80,
    SNPU_COMMAND_IDLE = 0xff,
    SNPU_COMMAND_ABSOLUTE_LINK = 1u << 16,
    SNPU_COMMAND_COMPLETION_INTERRUPT = 1u << 22
};
extern volatile uint32_t open_cfw_gx8002_snpu_task_words[0x5a0 / 4];
void open_cfw_gx8002_snpu_tcb_init(void)
{
    for (uint32_t task=0; task<10; ++task) {
        uint32_t offset=task*144;
        for (uint32_t entry=0; entry<8; ++entry) {
            uint32_t command=offset+0x20+entry*12;
            uintptr_t next=(uintptr_t)&open_cfw_gx8002_snpu_task_words[(offset+0x2c+entry*12)/4];
            open_cfw_gx8002_snpu_task_words[command/4]=(SNPU_COMMAND_ABSOLUTE_LINK | SNPU_COMMAND_BASE_SLOT_0)+entry;
            open_cfw_gx8002_snpu_task_words[(command+4)/4]=(uint32_t)next & UINT32_C(0x0fffffff);
        }
        open_cfw_gx8002_snpu_task_words[(offset+0x80)/4]=SNPU_COMMAND_ABSOLUTE_LINK | (SNPU_COMMAND_BASE_SLOT_0+8);
        open_cfw_gx8002_snpu_task_words[(offset+0x10)/4]=SNPU_COMMAND_COMPLETION_INTERRUPT | SNPU_COMMAND_ABSOLUTE_LINK | SNPU_COMMAND_IDLE;
    }
}
