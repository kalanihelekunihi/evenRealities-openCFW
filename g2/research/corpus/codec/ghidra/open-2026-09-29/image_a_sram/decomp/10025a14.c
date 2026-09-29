
void gx8002_clock_switch_1m(void)

{
  uint *puVar1;
  int *piVar2;
  uint uVar3;
  uint uVar4;
  undefined1 auStack_20 [8];
  undefined1 auStack_18 [8];
  
  gx8002_memcpy(auStack_20,uRam10025a7c,0x10);
  gx8002_clock_source_select(auStack_20);
  gx8002_clock_source_select(auStack_18);
  gx8002_clock_lowpower_init_shared();
  puVar1 = puRam10025a80;
  uVar4 = 0xb;
  do {
    uVar3 = gx8002_clock_gate_query_fixed(uVar4);
    if (uVar3 != 0xffffffff) {
      *puVar1 = (uVar3 & 1) << (uVar4 & 0x3f) | *puVar1;
    }
    piVar2 = piRam10025a84;
    uVar4 = uVar4 + 1;
  } while (uVar4 != 0x1a);
  gx8002_audio_lowpower_divider();
  gx8002_clock_module_divider_set(10,0);
  if (*piVar2 == 1) {
    *piVar2 = 0;
    gx8002_clock_pll_wait(piVar2);
    *piVar2 = 1;
  }
  return;
}

