/* WSF OS hosted on a QP/C active object ("WsfOs", assertion module string at
 * ROM 0x334548), reconstructed from the 2.2.6.10 EM9305 disassembly
 * (g2/research/corpus/em9305/objdump/open-2026-09-29).
 *
 * Stock ranges:
 *   0x314068..0x31408a  WsfOsInitOnly: clear the WSF OS context, construct the AO
 *   0x3140a8..0x3140b0  store the task-init callback (RAM 0x8019e4)
 *   0x3140d0..0x314112  WsfOsStartOnly: start the AO at the next QF priority
 *   0x333c44..0x333d16  AO state: entry runs the init callback; signal 8 services
 *                       messages, expired timers and per-handler event bits
 *   0x333d7c..0x333db6  wsfOsRunIdleTasks
 *   0x333db8..0x333dc2  AO initial pseudo-state
 *
 * WSF OS context at RAM 0x805ff4 (0x7c bytes, cleared by WsfOsInitOnly):
 *   +0x00 handler table [16]      (0x805ff4, WsfOsSetNextHandler 0x3140b4)
 *   +0x40 handler event bits [16] (0x806034, uint16 each)
 *   +0x60 message queue           (0x806054); +0x68 task event mask byte (0x80605c)
 *   +0x69 handler count           (0x80605d)
 *   +0x6c idle task table [3]     (0x806060, count byte 0x80606c, pending flag 0x80606d)
 * The AO object (36 B) is RAM 0x80139c and its 16-entry queue RAM 0x80faac,
 * both stock addresses that other units already address absolutely.
 *
 * Profile g2-em9305-1. */
#include <stddef.h>
#include <stdint.h>

typedef uint16_t g2_em_qsignal;
typedef struct {
    g2_em_qsignal sig;
    uint8_t pool_id;
    uint8_t volatile ref;
} g2_em_qevt;
typedef uint32_t g2_em_qstate;
struct g2_em_qactive;
typedef g2_em_qstate (*g2_em_qstate_handler)(struct g2_em_qactive *me, const g2_em_qevt *e);
typedef struct {
    void (*init)(struct g2_em_qactive *me);
    void (*dispatch)(struct g2_em_qactive *me, const g2_em_qevt *e);
    void (*start)(struct g2_em_qactive *me, uint32_t prio, const g2_em_qevt **qsto,
                  uint32_t qlen, void *stksto, uint32_t stksize, const void *par);
    uint32_t (*post)(struct g2_em_qactive *me, const g2_em_qevt *e, uint32_t margin);
} g2_em_qactive_vtable;
struct g2_em_qactive {
    const g2_em_qactive_vtable *vptr; /* +0 */
    uintptr_t state;                  /* +4 */
    uintptr_t temp;                   /* +8 */
    uint8_t rest[24];
};

enum { Q_ENTRY_SIG = 1, WSF_OS_DISPATCH_SIG = 8 };
enum { Q_RET_SUPER = 0, Q_RET_HANDLED = 3, Q_RET_TRAN = 8 };
enum { WSF_EVT_MSG = 0x01, WSF_EVT_TIMER = 0x02, WSF_EVT_HANDLER = 0x04 };

#define WSF_OS_CONTEXT       0x805ff4u
#define WSF_OS_HANDLERS      0x805ff4u
#define WSF_OS_HANDLER_EVTS  0x806034u
#define WSF_OS_MSG_QUEUE     0x806054u
#define WSF_OS_TASK_EVENTS   0x80605cu
#define WSF_OS_IDLE_TASKS    0x806060u
#define WSF_OS_IDLE_COUNT    0x80606cu
#define WSF_OS_IDLE_PENDING  0x80606du
#define WSF_OS_INIT_CBACK    0x8019e4u
#define WSF_OS_AO            ((struct g2_em_qactive *)(uintptr_t)0x80139cu)
#define WSF_OS_AO_QUEUE      ((const g2_em_qevt **)(uintptr_t)0x80faacu)

typedef void (*wsf_handler_t)(uint32_t event, uintptr_t msg);
typedef uint32_t (*wsf_init_cback_t)(uint32_t incoming);
typedef uint32_t (*wsf_idle_task_t)(void);

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes); /* 0x33301c */
extern void QActive_ctor(struct g2_em_qactive *me, g2_em_qstate_handler initial);     /* 0x310d18 */
extern g2_em_qstate QHsm_top(struct g2_em_qactive *me, const g2_em_qevt *e);         /* 0x311550 */
extern void opencfw_em9305_assert(uint32_t module, uint32_t line);                   /* 0x3117d8 */
extern uint32_t g2_em_qf_next_priority
    __attribute__((section(".bss.opencfw_qf_next_priority_8012bc")));               /* 0x8012bc */
extern uint32_t opencfw_em9305_wsf_critical_enter(void);                             /* 0x313f54 */
extern uint32_t opencfw_em9305_wsf_critical_exit(void);                              /* 0x313f6c */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue, uintptr_t handler); /* 0x313ff0 */
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);                   /* 0x314014 */
extern uintptr_t opencfw_em9305_wsf_timer_expired(void);                             /* 0x3142c8 */
extern uint32_t opencfw_em9305_wsf_timer_periodic(void);                             /* 0x333e4c */
extern uint32_t opencfw_em9305_controller_initialize_stack(uint32_t incoming);       /* 0x302a20 */

static const char wsf_os_module[] = "WsfOs"; /* ROM 0x334548 */

static g2_em_qstate wsf_os_active_333c44(struct g2_em_qactive *me, const g2_em_qevt *e);

/* Native 0x333db8: initial pseudo-state, transition to the active state. */
static g2_em_qstate wsf_os_initial_333db8(struct g2_em_qactive *me, const g2_em_qevt *e)
{
    (void)e;
    me->temp = (uintptr_t)&wsf_os_active_333c44;
    return Q_RET_TRAN;
}

/* Native 0x333c44. The timer update runs on entry and again before return. */
static g2_em_qstate wsf_os_active_333c44(struct g2_em_qactive *me, const g2_em_qevt *e)
{
    g2_em_qstate ret;
    uint8_t handler_id;

    (void)opencfw_em9305_wsf_timer_periodic();
    if (e->sig == WSF_OS_DISPATCH_SIG) {
        uint32_t events;

        (void)opencfw_em9305_wsf_critical_enter();
        events = *(volatile uint8_t *)(uintptr_t)WSF_OS_TASK_EVENTS;
        *(volatile uint8_t *)(uintptr_t)WSF_OS_TASK_EVENTS = 0u;
        (void)opencfw_em9305_wsf_critical_exit();

        if (events & WSF_EVT_MSG) {
            uintptr_t msg;
            while ((msg = opencfw_em9305_wsf_event_remove(WSF_OS_MSG_QUEUE,
                                                          (uintptr_t)&handler_id)) != 0u) {
                wsf_handler_t handler = (wsf_handler_t)(uintptr_t)
                    *(volatile uint32_t *)(uintptr_t)(WSF_OS_HANDLERS + handler_id * 4u);
                handler(0u, msg);
                (void)opencfw_em9305_wsf_event_release(msg);
            }
        }
        if (events & WSF_EVT_TIMER) {
            uintptr_t timer;
            while ((timer = opencfw_em9305_wsf_timer_expired()) != 0u) {
                uint32_t id = *(volatile uint8_t *)(timer + 12u);
                wsf_handler_t handler = (wsf_handler_t)(uintptr_t)
                    *(volatile uint32_t *)(uintptr_t)(WSF_OS_HANDLERS + id * 4u);
                handler(0u, timer + 4u);
            }
        }
        if (events & WSF_EVT_HANDLER) {
            volatile uint32_t *handlers = (volatile uint32_t *)(uintptr_t)WSF_OS_HANDLERS;
            volatile uint16_t *bits = (volatile uint16_t *)(uintptr_t)WSF_OS_HANDLER_EVTS;
            for (uint32_t i = 0u; i < 16u; i++) {
                if (bits[i] != 0u && handlers[i] != 0u) {
                    uint32_t pending;
                    (void)opencfw_em9305_wsf_critical_enter();
                    pending = bits[i];
                    bits[i] = 0u;
                    (void)opencfw_em9305_wsf_critical_exit();
                    ((wsf_handler_t)(uintptr_t)handlers[i])(pending, 0u);
                }
            }
        }
        ret = Q_RET_HANDLED;
    } else if (e->sig == Q_ENTRY_SIG) {
        wsf_init_cback_t init = (wsf_init_cback_t)(uintptr_t)
            *(volatile uint32_t *)(uintptr_t)WSF_OS_INIT_CBACK;
        if (init != NULL)
            (void)init(WSF_OS_INIT_CBACK); /* stock leaves r0 = 0x8019e4 */
        ret = Q_RET_HANDLED;
    } else {
        me->temp = (uintptr_t)&QHsm_top;
        ret = Q_RET_SUPER;
    }
    (void)opencfw_em9305_wsf_timer_periodic();
    return ret;
}

/* Native 0x314068: WsfOsInitOnly. */
void wsf_os_init_only_314068(void)
{
    (void)opencfw_em9305_memset((void *)(uintptr_t)WSF_OS_CONTEXT, 0u, 0x7cu);
    QActive_ctor(WSF_OS_AO, wsf_os_initial_333db8);
}

/* Native 0x3140a8: store the task-init callback run on AO entry. */
void wsf_os_set_init_cback_3140a8(wsf_init_cback_t callback)
{
    *(volatile uint32_t *)(uintptr_t)WSF_OS_INIT_CBACK = (uint32_t)(uintptr_t)callback;
}

/* Native 0x3140d0: WsfOsStartOnly. Assertion 653 checks the constructor ran;
 * Q_onAssert returns, so the start proceeds as in stock. */
void wsf_os_start_only_3140d0(void)
{
    uint32_t prio;

    if (WSF_OS_AO->vptr == NULL)
        opencfw_em9305_assert((uint32_t)(uintptr_t)wsf_os_module, 653u);
    prio = g2_em_qf_next_priority;
    g2_em_qf_next_priority = prio - 1u;
    WSF_OS_AO->vptr->start(WSF_OS_AO, (uint8_t)prio, WSF_OS_AO_QUEUE, 16u, NULL, 0u, NULL);
}

/* Native 0x30460c: veneer, tail call to WsfOsInitOnly. */
void wsf_os_init_only_veneer_30460c(void)
{
    wsf_os_init_only_314068();
}

/* Native 0x304610: register the stack init callback (0x302a20), then start. */
void wsf_os_register_start_304610(void)
{
    wsf_os_set_init_cback_3140a8(opencfw_em9305_controller_initialize_stack);
    wsf_os_start_only_3140d0();
}

/* Native 0x333d7c: run registered idle tasks (table filled by 0x31408c) while
 * the pending flag is set; the flag becomes bit 0 of the last result. */
uint32_t wsfOsRunIdleTasks(void)
{
    volatile uint8_t *pending = (volatile uint8_t *)(uintptr_t)WSF_OS_IDLE_PENDING;
    volatile uint8_t *count = (volatile uint8_t *)(uintptr_t)WSF_OS_IDLE_COUNT;
    volatile uint32_t *tasks = (volatile uint32_t *)(uintptr_t)WSF_OS_IDLE_TASKS;
    uint32_t result = 0u;

    if (*pending == 0u)
        return 0u;
    if (*count != 0u) {
        for (uint32_t i = 0u; i < *count; i++) {
            wsf_idle_task_t task = (wsf_idle_task_t)(uintptr_t)tasks[i];
            if (task != NULL)
                result = (result & 1u) | task();
        }
    }
    result &= 1u;
    *pending = (uint8_t)result;
    return result;
}
