/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader TLSF pool initializer. */

typedef __UINT32_TYPE__ open_cfw_alloc_u32;
typedef __UINTPTR_TYPE__ open_cfw_alloc_uintptr;

enum {
    OPEN_CFW_ALLOC_POOL = 0x20081000U,
    OPEN_CFW_ALLOC_POOL_BYTES = 0x00070800U,
    OPEN_CFW_ALLOC_HANDLE = 0x2002718CU,
    OPEN_CFW_ALLOC_MEMSET_THUMB = 0x0041560DU,
    OPEN_CFW_ALLOC_CREATE_THUMB = 0x00417241U,
    OPEN_CFW_ALLOC_LOG_THUMB = 0x004176CFU,
    OPEN_CFW_ALLOC_LOG_TAG = 0x00434144U,
    OPEN_CFW_ALLOC_LOG_FORMAT = 0x004315C8U,
    OPEN_CFW_ALLOC_LOG_ARGUMENT = 0x00433CA4U,
    OPEN_CFW_ALLOC_LOG_FILE = 0x00434010U,
    OPEN_CFW_ALLOC_LOG_LINE = 0x13U
};

typedef void (*open_cfw_alloc_memset_fn)(void *, open_cfw_alloc_u32, open_cfw_alloc_u32);
typedef void *(*open_cfw_alloc_create_fn)(void *, open_cfw_alloc_u32);
typedef void (*open_cfw_alloc_log_fn)(open_cfw_alloc_u32, const void *, const void *, const void *, open_cfw_alloc_u32, const void *);

#if defined(OPEN_CFW_ALLOCATOR_INIT_HOST)
void *open_cfw_allocator_init_host_pool(void);
void **open_cfw_allocator_init_host_handle(void);
void open_cfw_allocator_init_host_memset(void *, open_cfw_alloc_u32, open_cfw_alloc_u32);
void *open_cfw_allocator_init_host_create(void *, open_cfw_alloc_u32);
void open_cfw_allocator_init_host_log(open_cfw_alloc_u32, open_cfw_alloc_uintptr, open_cfw_alloc_uintptr, open_cfw_alloc_uintptr, open_cfw_alloc_u32, open_cfw_alloc_uintptr);
#endif

__attribute__((used, noinline))
open_cfw_alloc_u32 open_cfw_bootloader_allocator_init_41fd70(void)
{
    void *pool;
    void *handle;
#if defined(OPEN_CFW_ALLOCATOR_INIT_HOST)
    pool = open_cfw_allocator_init_host_pool();
    open_cfw_allocator_init_host_memset(pool, OPEN_CFW_ALLOC_POOL_BYTES, 0U);
    handle = open_cfw_allocator_init_host_create(pool, OPEN_CFW_ALLOC_POOL_BYTES);
    *open_cfw_allocator_init_host_handle() = handle;
    open_cfw_allocator_init_host_log(4U, OPEN_CFW_ALLOC_LOG_TAG,
        OPEN_CFW_ALLOC_LOG_FORMAT, OPEN_CFW_ALLOC_LOG_ARGUMENT,
        OPEN_CFW_ALLOC_LOG_LINE, OPEN_CFW_ALLOC_LOG_FILE);
#else
    pool = (void *)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_POOL;
    ((open_cfw_alloc_memset_fn)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_MEMSET_THUMB)(pool, OPEN_CFW_ALLOC_POOL_BYTES, 0U);
    handle = ((open_cfw_alloc_create_fn)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_CREATE_THUMB)(pool, OPEN_CFW_ALLOC_POOL_BYTES);
    *(void **)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_HANDLE = handle;
    ((open_cfw_alloc_log_fn)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_LOG_THUMB)(
        4U,
        (const void *)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_LOG_TAG,
        (const void *)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_LOG_FORMAT,
        (const void *)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_LOG_ARGUMENT,
        OPEN_CFW_ALLOC_LOG_LINE,
        (const void *)(open_cfw_alloc_uintptr)OPEN_CFW_ALLOC_LOG_FILE);
#endif
    return 0U;
}
