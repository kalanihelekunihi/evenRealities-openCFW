/* SPDX-License-Identifier: MIT
 * Reconstructed wrappers 41fd70,41552c,415558; pinned BSD TLSF core.
 * Raw stock locking semantics: allocation lock failure returns NULL;
 * free lock failure leaves the allocation live. No extra synchronization.
 */
#include "allocator.h"
#include "upstream/tlsf.h"
#include "../filesystem/file_services.h"
#include <string.h>
#define CORE (*(tlsf_t volatile *)(uintptr_t)0x2002718cu)
#define MUTEX (*(uintptr_t volatile *)(uintptr_t)0x20027130u)
extern void opencfw_boot_allocator_log(uint32_t);
void *opencfw_boot_allocator_core(void) {return CORE;}
uint32_t opencfw_boot_allocator_init(void) {
    void *arena=(void *)(uintptr_t)OPENCFW_BOOT_ARENA_BASE;
    memset(arena,0,OPENCFW_BOOT_ARENA_SIZE);
    CORE=tlsf_create_with_pool(arena,OPENCFW_BOOT_ARENA_SIZE);
    opencfw_boot_allocator_log(0x13u);
    return 0;
}
void *opencfw_boot_fs_alloc(uint32_t bytes) {
    void *result=0;
    if(!opencfw_boot_fs_mutex_acquire(MUTEX,1000u)) {
        result=tlsf_malloc(CORE,bytes);
        opencfw_boot_fs_mutex_release(MUTEX);
    }
    return result;
}
void opencfw_boot_fs_free(void *pointer) {
    if(!opencfw_boot_fs_mutex_acquire(MUTEX,1000u)) {
        tlsf_free(CORE,pointer);
        opencfw_boot_fs_mutex_release(MUTEX);
    }
}
