/* SPDX-License-Identifier: MIT
 * Locked418a98..418ad4 deferred deletion drain. IncomingR3 returns inR0.
 */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern uint32_t opencfw_boot_list_unlink(uint32_t *);
extern void opencfw_boot_thread_release_storage(uint32_t *);
uint32_t opencfw_boot_idle_cleanup(uint32_t a,uint32_t b,uint32_t c,uint32_t carry) {
 (void)a;(void)b;(void)c;
 while(W(0x20027140u)!=0u) {
  opencfw_bl_kernel_enter();
  uint32_t *head=(uint32_t *)(uintptr_t)W(0x20026f7cu);
  uint32_t *tcb=(uint32_t *)(uintptr_t)head[3];
  (void)opencfw_boot_list_unlink(tcb+1);
  --W(0x20027144u);--W(0x20027140u);
  opencfw_bl_kernel_exit();
  opencfw_boot_thread_release_storage(tcb);
 }
 return carry;
}
