# P2-9127 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 12 original-byte queue-drain cases over empty, one-node, and three-node queues, executing original pop/release/pool/gate instructions.
- The independent reverse-pool/tag oracle matched queue links and tags, returned dequeue ID, pool state, and register/SP/PC checks. The gate ran even on empty-pop paths; with initial nesting zero the tested helper behavior cleared the mask as specified.

Limitations:

- Synthetic queues, pools, and mask state only; no concurrent queue operations, physical preemption, or lifecycle guarantee.
