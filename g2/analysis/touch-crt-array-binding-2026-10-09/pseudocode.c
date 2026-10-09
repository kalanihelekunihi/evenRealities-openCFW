/* Instruction/source interpretation only; not production firmware source. */
typedef unsigned int u32;
typedef void (*fn)(void);
void reset_load_suffix_467E(void) {
    memcpy((void *)0x20000400, (void *)0x3300, 192);
    *(volatile u32 *)0xE000ED08 = 0x20000400;
    /* Records actually read from imageB578..B58C; counts are words. */
    for (u32 i=0; i<241; ++i)
        ((u32 *)0x200004C0)[i] = ((u32 *)0xB58C)[i];
    for (u32 i=0; i<428; ++i) ((u32 *)0x200008A8)[i] = 0;
    reset_c_3464(); /* Test stops before this call. */
}
void frame_dummy_3434(void) {
    /* Weak __register_frame_info resolves0; registration skipped. */
    register_tm_clones_33E0(); /* Empty interval20000884..20000884. */
}
void dtors_aux_3408(void) {
    unsigned char *completed=(unsigned char *)0x200008A8;
    if (*completed) return;
    deregister_tm_clones_33C0(); /* Empty interval, no external call. */
    /* Weak __deregister_frame_info resolves0. */
    *completed=1;
}
/* Copy record binds init_array[0] at2000087C to3435,
 * fini_array[0] at20000880 to3409. This does not make exit dispatch fini. */
