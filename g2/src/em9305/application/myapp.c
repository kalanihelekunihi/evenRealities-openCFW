/* EM9305 product active object "MyApp" (assertion module string "MyApp" at
 * ROM 0x334514). First-party application code built on QP/C 6.5.1.
 * Native 0x30ea08..0x30eb0a: constructor, reset state, active state,
 * initial transition, event-post helper, start and signal classifier.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* QP/C 6.5.1 layout with the EM port configuration (Q_SIGNAL_SIZE = 2). */
typedef uint16_t g2_em_qsignal;
typedef struct {
    g2_em_qsignal sig;      /* +0 */
    uint8_t pool_id;        /* +2 */
    uint8_t volatile ref;   /* +3 */
} g2_em_qevt;
_Static_assert(sizeof(g2_em_qevt) == 4, "QEvt size");

typedef struct {
    g2_em_qevt super;       /* +0 */
    uint32_t param;         /* +4 */
} g2_em_myapp_evt;
_Static_assert(sizeof(g2_em_myapp_evt) == 8, "MyApp event size");

typedef uint32_t g2_em_qstate;
struct g2_em_qactive;
typedef g2_em_qstate (*g2_em_qstate_handler)(struct g2_em_qactive *me, const g2_em_qevt *e);

typedef struct {
    void (*init)(struct g2_em_qactive *me);                                   /* +0 */
    void (*dispatch)(struct g2_em_qactive *me, const g2_em_qevt *e);          /* +4 */
    void (*start)(struct g2_em_qactive *me, uint32_t prio, const g2_em_qevt **qsto,
                  uint32_t qlen, void *stksto, uint32_t stksize, const void *par); /* +8 */
    bool (*post)(struct g2_em_qactive *me, const g2_em_qevt *e, uint32_t margin); /* +12 */
} g2_em_qactive_vtable;

struct g2_em_qactive {
    const g2_em_qactive_vtable *vptr; /* +0 */
    uintptr_t state;                  /* +4 */
    uintptr_t temp;                   /* +8 */
    uint8_t rest[24];                 /* +12 .. sizeof(QActive) = 36 */
};
_Static_assert(sizeof(struct g2_em_qactive) == 36, "QActive size (libraries.md)");

/* QEP reserved signals and return codes (QP/C 6.5.1). */
enum { G2_EM_Q_EMPTY_SIG = 0, G2_EM_Q_ENTRY_SIG = 1, G2_EM_Q_EXIT_SIG = 2, G2_EM_Q_INIT_SIG = 3 };
enum { G2_EM_Q_RET_SUPER = 0, G2_EM_Q_RET_HANDLED = 3, G2_EM_Q_RET_TRAN = 8 };
/* MyApp user signals. */
enum { G2_EM_MYAPP_IDLE_SIG = 4, G2_EM_MYAPP_RESET_SIG = 5, G2_EM_MYAPP_IGNORED_SIG = 255 };
#define G2_EM_QF_NO_MARGIN 0xffffu

static const char g2_em_myapp_module[] = "MyApp"; /* ROM 0x334514 */

extern struct g2_em_qactive g2_em_myapp_ao;       /* RAM 0x801970 */
extern uint32_t g2_em_qf_next_priority;           /* RAM 0x8012bc, decremented per AO start */
extern const g2_em_qevt *g2_em_myapp_queue[4];    /* RAM 0x80f97c */

extern void QActive_ctor(struct g2_em_qactive *me, g2_em_qstate_handler initial); /* 0x310d18 */
extern g2_em_qstate QHsm_top(struct g2_em_qactive *me, const g2_em_qevt *e);       /* 0x311550 */
extern uintptr_t opencfw_em9305_qpc_event_allocate(uint32_t bytes, uint32_t margin, uint32_t signal); /* QF_newX_ 0x311060 */
extern void opencfw_em9305_assert(uint32_t module, uint32_t line); /* Q_onAssert 0x3117d8 (returns) */
extern _Noreturn void em9305_rom_system_reset_103f14(void);

static g2_em_qstate myapp_active_30ea34(struct g2_em_qactive *me, const g2_em_qevt *e);

/* Native 0x30ea18: entering this state resets the chip. */
static g2_em_qstate myapp_reset_30ea18(struct g2_em_qactive *me, const g2_em_qevt *e)
{
    if (e->sig == G2_EM_Q_ENTRY_SIG) em9305_rom_system_reset_103f14();
    me->temp = (uintptr_t)&QHsm_top;
    return G2_EM_Q_RET_SUPER;
}

/* Native 0x30ea84: initial pseudo-state, transition to the active state. */
static g2_em_qstate myapp_initial_30ea84(struct g2_em_qactive *me, const g2_em_qevt *e)
{
    (void)e;
    me->temp = (uintptr_t)&myapp_active_30ea34;
    return G2_EM_Q_RET_TRAN;
}

/* Native 0x30ea90: allocate an 8-byte event and post it FIFO to MyApp. */
static void myapp_post_30ea90(uint32_t sig, uint32_t param)
{
    g2_em_myapp_evt *evt = (g2_em_myapp_evt *)opencfw_em9305_qpc_event_allocate(
        sizeof(g2_em_myapp_evt), G2_EM_QF_NO_MARGIN, sig);
    evt->param = param;
    (void)g2_em_myapp_ao.vptr->post(&g2_em_myapp_ao, &evt->super, G2_EM_QF_NO_MARGIN);
}

/* Native 0x30eafc: 0 = handled (IDLE), 2 = reset transition, 1 = unhandled.
 * The parameter word is passed but not used. */
static uint32_t myapp_classify_30eafc(uint32_t sig, uint32_t param)
{
    (void)param;
    if (sig == G2_EM_MYAPP_IDLE_SIG) return 0u;
    return (sig == G2_EM_MYAPP_RESET_SIG) ? 2u : 1u;
}

/* Native 0x30ea34: active state. Entry posts IDLE to itself. */
static g2_em_qstate myapp_active_30ea34(struct g2_em_qactive *me, const g2_em_qevt *e)
{
    uint32_t sig = e->sig;
    uint32_t action;

    if (sig == G2_EM_Q_EXIT_SIG || sig == G2_EM_Q_INIT_SIG || sig == G2_EM_MYAPP_IGNORED_SIG)
        goto super;
    if (sig == G2_EM_Q_ENTRY_SIG) {
        myapp_post_30ea90(G2_EM_MYAPP_IDLE_SIG, 0u);
        return G2_EM_Q_RET_HANDLED;
    }
    if (sig == G2_EM_Q_EMPTY_SIG) goto super;
    action = myapp_classify_30eafc(sig, ((const g2_em_myapp_evt *)e)->param);
    if (action == 2u) {
        me->temp = (uintptr_t)&myapp_reset_30ea18;
        return G2_EM_Q_RET_TRAN;
    }
    if (action != 1u) return G2_EM_Q_RET_HANDLED;
super:
    me->temp = (uintptr_t)&QHsm_top;
    return G2_EM_Q_RET_SUPER;
}

/* Stock 0x0030EA08 (application_module_myapp: MyApp constructor) */
void myapp_ctor_30ea08(void)
{
    QActive_ctor(&g2_em_myapp_ao, myapp_initial_30ea84);
}

/* Native 0x30eabc: start MyApp with the next free priority and a 4-entry queue.
 * Assertion ID 181 checks that the constructor ran (vptr set); it may return. */
void myapp_start_30eabc(void)
{
    uint32_t prio;

    if (g2_em_myapp_ao.vptr == NULL)
        opencfw_em9305_assert((uint32_t)(uintptr_t)g2_em_myapp_module, 181u);
    prio = g2_em_qf_next_priority;
    g2_em_qf_next_priority = prio - 1u;
    g2_em_myapp_ao.vptr->start(&g2_em_myapp_ao, (uint8_t)prio, g2_em_myapp_queue, 4u,
                               NULL, 0u, NULL);
}
