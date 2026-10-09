/* Analysis-only reconstructed observable prefix, not production source. */
struct queue_prefix { unsigned front,ring; unsigned char end,head,tail,nFree,nMin; };
void init_310f5c(struct queue_prefix *q,unsigned ring,unsigned len) {
 q->ring=ring; q->front=0; q->end=(unsigned char)len;
 if(len!=0){ q->head=0;q->tail=0; }
 q->nFree=(unsigned char)(len+1);q->nMin=q->nFree;
}
/* Scheduler continuation ONLY. Candidate-producing instruction unresolved. */
unsigned scheduler_tail(unsigned candidate,unsigned active,unsigned lock) {
 if(candidate<=active || candidate<=lock)return 0;
 if(candidate>=17) assert_3117d8(0x33451c,410);
 nextPrio=(unsigned char)candidate;return (unsigned char)candidate;
}
