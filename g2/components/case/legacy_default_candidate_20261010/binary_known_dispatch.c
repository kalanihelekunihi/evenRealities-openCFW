/* SPDX-License-Identifier: MIT
 * Test-only routing of bounded binary source candidates.
 * Returns false where a coherent full branch/lower contract is absent.
 */
#include <stdbool.h>
#include <stdint.h>
extern uint32_t case_binary_forward_candidate(const uint8_t *,uint32_t,uint32_t);
extern uint32_t case_binary_3d_candidate(const uint8_t *,uint32_t,uint32_t);
extern uint32_t case_binary_local_four_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_unknown_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_14_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_3e_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_3f_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_51_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_56_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_5e_candidate(const uint8_t *,uint32_t);
extern uint32_t case_binary_5f_candidate(const uint8_t *,uint32_t);
bool case_binary_known_dispatch(const uint8_t *p,uint32_t n,uint32_t mode,uint32_t *result)
{
    if(p[2]!=2) {
        *result=p[0]==0x3d ? case_binary_3d_candidate(p,n,mode)
                           : case_binary_forward_candidate(p,n,mode);
        return true;
    }
    switch(p[0]) {
    case 0x06:case 0x41: /* stops before unresolved ee/ff legacy lower */
        return false;
    case 0x50:case 0x5c:case 0x5d:case 0x68:
        *result=case_binary_local_four_candidate(p,n);return true;
    case 0x14:*result=case_binary_14_candidate(p,n);return true;
    case 0x3e:*result=case_binary_3e_candidate(p,n);return true;
    case 0x3f:*result=case_binary_3f_candidate(p,n);return true;
    case 0x51:*result=case_binary_51_candidate(p,n);return true;
    case 0x56:*result=case_binary_56_candidate(p,n);return true;
    case 0x5e:*result=case_binary_5e_candidate(p,n);return true;
    case 0x5f:*result=case_binary_5f_candidate(p,n);return true;
    default:*result=case_binary_unknown_candidate(p,n);return true;
    }
}
