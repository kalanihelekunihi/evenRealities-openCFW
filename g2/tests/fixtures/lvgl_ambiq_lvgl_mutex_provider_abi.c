/* SPDX-License-Identifier: MIT */
#include "src/osal/lv_os.h"

_Static_assert(sizeof(void *) == 4, "G2 pointer ABI changed");
_Static_assert(sizeof(lv_result_t) == 1, "G2 short-enum ABI changed");
_Static_assert(sizeof(lv_mutex_t) == 8, "G2 lv_mutex_t ABI changed");
_Static_assert(__builtin_offsetof(lv_mutex_t, xIsInitialized) == 0,
               "G2 mutex initialization offset changed");
_Static_assert(__builtin_offsetof(lv_mutex_t, xMutex) == 4,
               "G2 mutex handle offset changed");

lv_result_t open_cfw_mutex_probe_init(lv_mutex_t * mutex) { return lv_mutex_init(mutex); }
lv_result_t open_cfw_mutex_probe_lock(lv_mutex_t * mutex) { return lv_mutex_lock(mutex); }
lv_result_t open_cfw_mutex_probe_unlock(lv_mutex_t * mutex) { return lv_mutex_unlock(mutex); }
lv_result_t open_cfw_mutex_probe_delete(lv_mutex_t * mutex) { return lv_mutex_delete(mutex); }
