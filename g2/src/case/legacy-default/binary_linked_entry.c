/* SPDX-License-Identifier: MIT
 * Test-only entry around binary_known_dispatch, for linked stock/source oracle.
 */
#include <stdbool.h>
#include <stdint.h>
extern bool case_binary_known_dispatch(const uint8_t *,uint32_t,uint32_t,uint32_t *);
uint32_t case_binary_linked_entry(const uint8_t *p,uint32_t n,uint32_t mode)
{
    uint32_t result=0;
    if(!case_binary_known_dispatch(p,n,mode,&result)) return 0xdeadbeefu;
    return result;
}
