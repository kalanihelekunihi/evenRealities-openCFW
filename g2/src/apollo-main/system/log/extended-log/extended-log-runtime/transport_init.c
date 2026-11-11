/* Stock-derived logger transport initialization 0x44895e/e8/8c74.
 * Product RAM literals are authenticated from the locked Apollo image. */
#include <stdint.h>
#include <stddef.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_elog_async_enabled[] __asm__("g2_elog_async_enabled");
extern unsigned char g2ref_g2_elog_default_level[] __asm__("g2_elog_default_level");
extern unsigned char g2ref_g2_elog_pending_head[] __asm__("g2_elog_pending_head");
extern unsigned char g2ref_g2_elog_pending_tail[] __asm__("g2_elog_pending_tail");
extern unsigned char g2ref_g2_elog_stats[] __asm__("g2_elog_stats");
extern unsigned char g2ref_g2_stock_ram_20074570[] __asm__("g2_stock_ram_20074570");
extern unsigned char g2ref_g2_stock_ram_202d3fc8[] __asm__("g2_stock_ram_202d3fc8");

typedef struct LogInitNode {
    struct LogInitNode *next;
    uint32_t state;
    uint16_t length,level;
    uint8_t mode,payload[256];
} LogInitNode;
_Static_assert(sizeof(LogInitNode)==272 && offsetof(LogInitNode,payload)==13,
               "stock logger pool stride");
static LogInitNode *const pool=(LogInitNode *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_202d3fc8);
static LogInitNode *volatile *const free_head=(LogInitNode *volatile *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074570+0x4u);
static LogInitNode *volatile *const pending_head=(LogInitNode *volatile *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_elog_pending_head);
static LogInitNode *volatile *const pending_tail=(LogInitNode *volatile *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_elog_pending_tail);
static volatile uint8_t *const enabled=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_elog_async_enabled);
static volatile uint8_t *const default_level=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_elog_default_level);
static volatile uint8_t *const stats=(volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_elog_stats);

static void publish_word(volatile uint32_t *word,uint32_t value) {
    *word=value;
    __asm__ volatile("dmb" ::: "memory");
}
/* Stock 0x0044895E (elog async node pool init) */
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
/* Stock 0x004489E8 (elog async pending-queue sentinel init) */
void g2_log_transport_pending_initialize(void) {
    LogInitNode *const sentinel=&pool[255];
    sentinel->next=0;
    *pending_head=sentinel;
    *pending_tail=sentinel;
    __asm__ volatile("dmb" ::: "memory");
}
/* Stock 0x00448C74 (elog async transport init) */
void g2_log_transport_initialize(void) {
    if(*enabled) return;
    g2_log_transport_pool_initialize();
    g2_log_transport_pending_initialize();
    for(uint32_t i=0;i<48u;i++) stats[i]=0;
    *default_level=1;
    *enabled=1;
}
