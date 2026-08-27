# G2 bootloader runtime submit `0x0041649A` source closure

The complete 64-byte stock body `[0x0041649A,0x004164DA)` hashes to
`3da32489b13b78370fde01b22ef77515363ac2866a8baa24e444d03ae87ec0e9`.
Its sole direct caller is authenticated at `0x0042E80C`.

`runtime_submit_41649a.c` preserves the critical-context `-6`, invalid-input
`-4`, retained `0x0041937C(owner,4,arg,0,0)` call, success `0`, and backend
failure `-3` contract. Apple and Linux emit the same 54 unrelocated bytes;
two strict relocations bind the source-owned critical-context provider and the
retained submission backend. Host, target, dual-profile, redirect, manifest,
and package gates pass offline. Hardware execution is blocked by unavailable
authorized responsive G2 evidence.
