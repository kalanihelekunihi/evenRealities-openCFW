#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "../../../components/em9305/qpc_queue_candidate/qequeue_init.c"
int main(void) {
    QEQueue q;
    QEvt const *ring[2] = {0};
    const unsigned lengths[] = {0u, 1u, 2u, 254u, 255u, 256u, 65535u};
    for (unsigned i = 0; i < sizeof lengths / sizeof lengths[0]; ++i) {
        memset(&q, 0xa5, sizeof q);
        QEQueue_init(&q, ring, lengths[i]);
        assert(q.frontEvt == 0);
        assert(q.ring == ring);
        assert(q.end == (uint8_t)lengths[i]);
        assert(q.head == (lengths[i] ? 0u : 0xa5u));
        assert(q.tail == (lengths[i] ? 0u : 0xa5u));
        assert(q.nFree == (uint8_t)(lengths[i] + 1u));
        assert(q.nMin == q.nFree);
    }
}
