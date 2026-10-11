/* Experimental stock-derived lock-free logger node queue, 0x448a0c/a8e/af0.
 * Requires product initialization of pool/free head and pending sentinel. */
#include <stdint.h>
#include <stddef.h>

typedef struct LogNode {
    struct LogNode *next;       /* 0x00 */
    uint32_t state;             /* 0x04: free=0, allocated=1, pending=2 */
    uint16_t length;            /* 0x08 */
    uint16_t level;             /* 0x0a */
    uint8_t mode;               /* 0x0c */
    uint8_t payload[256];      /* 0x0d */
} LogNode;
_Static_assert(offsetof(LogNode,payload)==13 && sizeof(LogNode)==272,
               "stock logger node layout and 4-byte tail padding");

static LogNode *volatile *const free_head=(LogNode *volatile *)(uintptr_t)0x20074574u;
static LogNode *volatile *const pending_tail=(LogNode *volatile *)(uintptr_t)0x2007413cu;
static volatile uint32_t *const stats=(volatile uint32_t *)(uintptr_t)0x2007342cu;

/* Word-aligned LDR/LDREX/STREX-compatible operations on the Cortex-M target. */
static LogNode *load_node(LogNode *volatile *p) {
    return __atomic_load_n(p,__ATOMIC_SEQ_CST);
}
static int cas_node(LogNode *volatile *p,LogNode **expected,LogNode *desired) {
    return __atomic_compare_exchange_n(p,expected,desired,0,
                                       __ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST);
}
static void publish_word(volatile uint32_t *p,uint32_t value) {
    *p=value;
    __asm__ volatile("dmb" ::: "memory");
}
static void publish_next(LogNode *node,LogNode *next) {
    *(LogNode *volatile *)node=next;
    __asm__ volatile("dmb" ::: "memory");
}
static void record_success(unsigned total,unsigned peak,unsigned attempts) {
    stats[total] += attempts-1u;
    if(stats[peak]<attempts) stats[peak]=attempts;
}
static void record_exhaustion(int also_empty) {
    stats[11]++;
    if(also_empty) stats[1]++;
}

uint8_t *g2_log_transport_node_allocate(void) {
    for(unsigned attempts=1;attempts<=1000;attempts++) {
        LogNode *head=load_node(free_head);
        if(!head) {stats[1]++;return 0;}
        LogNode *next=load_node((LogNode *volatile *)head);
        if(cas_node(free_head,&head,next)) {
            record_success(3,4,attempts);
            publish_word(&head->state,1);
            publish_next(head,0);
            return (uint8_t *)head;
        }
    }
    record_exhaustion(1);
    return 0;
}

void g2_log_transport_node_free(uint8_t *raw) {
    if(!raw) return;
    LogNode *node=(LogNode *)raw;
    publish_word(&node->state,0);
    for(unsigned attempts=1;attempts<=1000;attempts++) {
        LogNode *head=load_node(free_head);
        publish_next(node,head);
        if(cas_node(free_head,&head,node)) {
            record_success(5,6,attempts);
            return;
        }
    }
    record_exhaustion(0);
}

uint32_t g2_log_transport_node_enqueue(uint8_t *raw) {
    if(!raw) return 0;
    LogNode *node=(LogNode *)raw;
    publish_word(&node->state,2);
    publish_next(node,0);
    for(unsigned attempts=1;attempts<=10000;attempts++) {
        LogNode *tail=load_node(pending_tail);
        LogNode *next=load_node((LogNode *volatile *)tail);
        if(tail!=load_node(pending_tail)) continue;
        if(next) {
            (void)cas_node(pending_tail,&tail,next);
            continue;
        }
        LogNode *expected=0;
        if(cas_node((LogNode *volatile *)tail,&expected,node)) {
            record_success(7,8,attempts);
            (void)cas_node(pending_tail,&tail,node);
            return 1;
        }
    }
    record_exhaustion(1);
    g2_log_transport_node_free(raw);
    return 0;
}
