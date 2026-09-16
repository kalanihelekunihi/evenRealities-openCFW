/* SPDX-License-Identifier: MIT */
/* Pinned NationalChip queue writer adapted to backup's observed read order. */
#include "lvp_queue.h"
int LvpQueuePut(LVP_QUEUE *queue, const unsigned char *value)
{
    volatile LVP_QUEUE *q=queue;
    int tail=q->tail;
    int member=q->member_size;
    int size=q->size;
    int next=(tail+member)%size;
    if(next==q->head)return 0;
    if(member>0) {
        int i=0;
        for (;;) {
            int offset=(tail+i)%size;
            unsigned char *buffer=q->buffer;
            buffer[offset]=*value++;
            ++i;
            member=q->member_size;
            if(i>=member)break;
            tail=q->tail;
            size=q->size;
        }
        tail=q->tail;
        size=q->size;
        next=(tail+member)%size;
    }
    q->tail=next;
    return 1;
}
