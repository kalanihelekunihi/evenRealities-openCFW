/* Stock R1 application 0x514e0: link-context lookup for the BAE8 transport.
 * Keep the native full-word connection contract and volatile descriptor reads.
 * Supersedes the unused, narrower SDK blcm_link_ctx_get compilation unit. */
#include <stdint.h>
#include <stddef.h>
extern uint16_t ble_conn_state_conn_idx(uint16_t connection);
struct link_storage {
    void *volatile pool;
    volatile uint8_t maximum;
    uint8_t padding;
    volatile uint16_t size;
};
_Static_assert(offsetof(struct link_storage,maximum)==4,"stock capacity byte");
_Static_assert(offsetof(struct link_storage,size)==6,"stock context size");
_Static_assert(sizeof(struct link_storage)==8,"stock storage descriptor");

/* Startup RW descriptor at 0x20006534 points at three four-byte ZI contexts
 * beginning at 0x200086e4. Keep the opaque service prefix until its fields
 * have individual recovered interfaces. The observer and sender share this
 * single service allocation (native address 0x20006504). */
uint8_t r1_bae8_link_context_pool[3][4]
    __attribute__((section(".r1.bae8.pool"),aligned(4)));
struct link_storage r1_bae8_link_context_storage
    __attribute__((section(".r1.bae8.storage"),aligned(4)))={
        .pool=r1_bae8_link_context_pool,.maximum=3,.padding=0,.size=4
    };
struct bae8_service_storage {
    uint8_t prefix[40];
    struct link_storage *link_storage;
    void *event_handler;
};
_Static_assert(offsetof(struct bae8_service_storage,link_storage)==40,
               "stock service storage pointer");
_Static_assert(offsetof(struct bae8_service_storage,event_handler)==44,
               "stock service callback slot");
_Static_assert(sizeof(struct bae8_service_storage)==48,"stock service extent");
struct bae8_service_storage r1_native_bae8_service
    __attribute__((section(".r1.bae8.service"),aligned(4)))={
        .link_storage=&r1_bae8_link_context_storage
    };

uint32_t r1_native_bae8_context_get(void *storage,uint32_t connection,void *volatile *output)
{
    if (!output) return 14;
    *output=0;
    if (!storage) return 14;
    struct link_storage *view=storage;
    if (!view->pool) return 14;
    if (((volatile uint8_t *)storage)[6]&3u) return 7;
    /* The native index/validity chain rejects the full word before any flag
     * read. Guard before entering the SDK's narrower C interface. */
    uint8_t index=20;
    if (connection<20) index=(uint8_t)ble_conn_state_conn_idx((uint16_t)connection);
    if (index==20) return 5;
    if (view->maximum<=index) return 4;
    uint16_t size=view->size;
    uintptr_t pool=(uintptr_t)view->pool;
    *output=(void *)(pool+(uint32_t)index*size);
    return 0;
}
