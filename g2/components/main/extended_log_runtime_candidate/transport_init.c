/* Stock-derived logger transport initialization 0x44895e/e8/8c74.
 * Product RAM literals are authenticated from the locked Apollo image. */
#include <stdint.h>
#include <stddef.h>

typedef struct LogInitNode {
    struct LogInitNode *next;
    uint32_t state;
    uint16_t length,level;
    uint8_t mode,payload[256];
} LogInitNode;
_Static_assert(sizeof(LogInitNode)==272 && offsetof(LogInitNode,payload)==13,
               "stock logger pool stride");
static LogInitNode *const pool=(LogInitNode *)(uintptr_t)0x202d3fc8u;
static LogInitNode *volatile *const free_head=(LogInitNode *volatile *)(uintptr_t)0x20074574u;
static LogInitNode *volatile *const pending_head=(LogInitNode *volatile *)(uintptr_t)0x20074138u;
static LogInitNode *volatile *const pending_tail=(LogInitNode *volatile *)(uintptr_t)0x2007413cu;
static volatile uint8_t *const enabled=(volatile uint8_t *)(uintptr_t)0x20074fc0u;
static volatile uint8_t *const default_level=(volatile uint8_t *)(uintptr_t)0x20004546u;
static volatile uint8_t *const stats=(volatile uint8_t *)(uintptr_t)0x2007342cu;

static void publish_word(volatile uint32_t *word,uint32_t value) {
    *word=value;
    __asm__ volatile("dmb" ::: "memory");
}
void g2_log_transport_pool_initialize(void) {
    for(uint32_t i=0;i<254u;i++) {
        volatile uint8_t *bytes=(volatile uint8_t *)&pool[i];
        for(uint32_t j=0;j<272u;j++) bytes[j]=0;
        publish_word(&pool[i].state,0);
        pool[i].next=&pool[i+1];
        __asm__ volatile("dmb" ::: "memory");
    }
    publish_word(&pool[254].state,0);
    pool[254].next=0;
    publish_word(&pool[255].state,0);
    pool[255].next=0;
    *free_head=pool;
    __asm__ volatile("dmb" ::: "memory");
}
void g2_log_transport_pending_initialize(void) {
    LogInitNode *const sentinel=&pool[255];
    sentinel->next=0;
    *pending_head=sentinel;
    *pending_tail=sentinel;
    __asm__ volatile("dmb" ::: "memory");
}
void g2_log_transport_initialize(void) {
    if(*enabled) return;
    g2_log_transport_pool_initialize();
    g2_log_transport_pending_initialize();
    for(uint32_t i=0;i<48u;i++) stats[i]=0;
    *default_level=1;
    *enabled=1;
}
