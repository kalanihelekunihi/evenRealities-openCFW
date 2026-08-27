# G2 bootloader runtime create `0x004164DA` source closure

The complete 84-byte body `[0x004164DA,0x0041652E)` hashes to
`d2c1ca8cb76c2a512d9e0c4cd0575b7f83a787b4309ac5962328749877134890`;
the direct caller at `0x0042E25A` is pinned.

`runtime_create_4164da.c` rejects critical context, accepts only the exact
dynamic `(NULL,0)` or static `(storage,size>=32)` configurations, and binds
the retained static `0x00419978` and dynamic `0x004199BC` constructors. Both
reviewed compilers emit a 46-byte leaf under three strict relocations. Host,
target, redirect, manifest, and package gates pass offline. Live allocation
and scheduler behavior is blocked by unavailable authorized hardware evidence.
