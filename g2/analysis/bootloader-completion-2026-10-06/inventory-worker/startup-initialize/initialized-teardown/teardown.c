/* SPDX-License-Identifier: MIT
 * Reconstructed stock42e3ca..42e3e0, not a scheduler/quiescence proof.
 * Existing DFU42ddda reconstruction is tested alongside this manager entry.
 */
#include <stdint.h>
extern void opencfw_provider_416200(uintptr_t);
uint32_t opencfw_boot_manager_thread_deinit(void) {
 volatile uint32_t *handle=(volatile uint32_t *)(uintptr_t)0x200004fcu;
 uint32_t value=*handle;
 if(value) {
  /* Stock rereads the volatile handle before termination. */
  opencfw_provider_416200(*handle);
  *handle=0;
 }
 return 0;
}
