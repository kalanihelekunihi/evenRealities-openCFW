/* SPDX-License-Identifier: MIT
 * Bounded composition of independently compared legacy branches.
 * Valid command buffers have a routed branch for each opcode; this remains
 * an experimental composition, not the selected public handler.
 */
#include <stdbool.h>
#include <stdint.h>
extern uint32_t case_legacy_default_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a0_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a1_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a2_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a3_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a4_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_a5_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_aa_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_ab_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_ae_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_af_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_b0_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_d0_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_d1_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_d2_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_d3_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_d4_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_dd_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_df_branch(const uint8_t *,uint32_t);
extern uint32_t case_legacy_ee_prefix(const uint8_t *,uint32_t);
extern uint32_t case_legacy_ff_prefix(const uint8_t *,uint32_t);
bool case_legacy_known_dispatch(const uint8_t *command,uint32_t length,uint32_t *result)
{
    if (!command || !result) return false;
    uint32_t (*branch)(const uint8_t *,uint32_t)=0;
    switch(command[0]) {
    case 0xa0:branch=case_legacy_a0_branch;break;
    case 0xa1:branch=case_legacy_a1_branch;break;
    case 0xa2:branch=case_legacy_a2_branch;break;
    case 0xa3:branch=case_legacy_a3_branch;break;
    case 0xa4:branch=case_legacy_a4_branch;break;
    case 0xa5:branch=case_legacy_a5_branch;break;
    case 0xa6:case 0xa7:case 0xa8:case 0xa9:
    case 0xac:case 0xad:branch=case_legacy_default_branch;break;
    case 0xaa:branch=case_legacy_aa_branch;break;
    case 0xab:branch=case_legacy_ab_branch;break;
    case 0xae:branch=case_legacy_ae_branch;break;
    case 0xaf:branch=case_legacy_af_branch;break;
    case 0xb0:branch=case_legacy_b0_branch;break;
    case 0xd0:branch=case_legacy_d0_branch;break;
    case 0xd1:branch=case_legacy_d1_branch;break;
    case 0xd2:branch=case_legacy_d2_branch;break;
    case 0xd3:branch=case_legacy_d3_branch;break;
    case 0xd4:branch=case_legacy_d4_branch;break;
    case 0xdd:branch=case_legacy_dd_branch;break;
    case 0xdf:branch=case_legacy_df_branch;break;
    case 0xee:branch=case_legacy_ee_prefix;break;
    case 0xff:branch=case_legacy_ff_prefix;break;
    default:branch=case_legacy_default_branch;break;
    }
    *result=branch(command,length);
    return true;
}
