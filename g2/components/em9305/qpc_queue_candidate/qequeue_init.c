/* Bounded QEQueue_init candidate, derived from Quantum Leaps QP/C v6.5.1
 * src/qf/qf_qeq.c, commit 416dcec8820b9cdb5827497e645d0d9375db53c6.
 * Copyright (C) 2002-2018 Quantum Leaps, LLC. GPL-3.0-or-later or
 * commercial license; see the retained upstream source for full notice.
 * This is an isolated source candidate, not a linked G2 firmware provider.
 */
#include <stddef.h>
#include <stdint.h>

typedef struct QEvt QEvt;
typedef uint8_t QEQueueCtr;
typedef struct QEQueue {
    QEvt const * volatile frontEvt;
    QEvt const **ring;
    QEQueueCtr end;
    volatile QEQueueCtr head;
    volatile QEQueueCtr tail;
    volatile QEQueueCtr nFree;
    QEQueueCtr nMin;
} QEQueue;

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(QEQueue, frontEvt) == 0, "front offset");
_Static_assert(offsetof(QEQueue, ring) == 4, "ring offset");
_Static_assert(offsetof(QEQueue, end) == 8, "end offset");
_Static_assert(offsetof(QEQueue, head) == 9, "head offset");
_Static_assert(offsetof(QEQueue, tail) == 10, "tail offset");
_Static_assert(offsetof(QEQueue, nFree) == 11, "nFree offset");
_Static_assert(offsetof(QEQueue, nMin) == 12, "nMin offset");
#endif

void QEQueue_init(QEQueue * const me, QEvt const *qSto[],
                  uint_fast16_t const qLen)
{
    me->frontEvt = (QEvt const *)0;
    me->ring = &qSto[0];
    me->end = (QEQueueCtr)qLen;
    if (qLen != (uint_fast16_t)0) {
        me->head = (QEQueueCtr)0;
        me->tail = (QEQueueCtr)0;
    }
    me->nFree = (QEQueueCtr)(qLen + (uint_fast16_t)1);
    me->nMin = me->nFree;
}
