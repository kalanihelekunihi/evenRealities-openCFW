# Touch enable-control word A0BC

Accept only unsigned R0<=3 and either (R1==1 and unsigned R2<=1) or (((R1-2) modulo256)<=1 and R2==0). This preserves the eight-bit aliases for modes258/259. Success writes ((R1<<6)&255)|(R2&63) as one word at40010100+4*R0 and returnszero. Rejection returns004A0001 with no write. No helper or stack frame occurs. BodyA0BC..A0FA excludes the trailing NOP and literal pool.

168 original-instruction fixtures check boundaries, aliases, exact write address/value, return and SP. Memory is synthetic; device meaning and physical accesses remain unresolved. No canonical admission or C implementation.
