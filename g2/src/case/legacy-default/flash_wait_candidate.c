/* SPDX-License-Identifier: MIT
 * Stock 0x08004958 elapsed-tick wait. Tick 0x08004eac is already selected
 * CASE source. Scheduling, tick progression and real elapsed time are lower
 * runtime contracts.
 */
#include <stdint.h>
extern uint32_t case_tick_word2(void);

uint32_t case_binary_5e_wait(uint32_t timeout)
{
    uint32_t start=case_tick_word2();
    if(timeout!=UINT32_MAX)
        timeout+=*(volatile uint8_t *)(uintptr_t)0x20000118u;
    uint32_t elapsed;
    do {elapsed=case_tick_word2()-start;} while(elapsed<timeout);
    return elapsed;
}
