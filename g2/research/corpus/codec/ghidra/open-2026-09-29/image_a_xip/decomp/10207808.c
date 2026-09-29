
undefined4 gx8002_power_suspend(uint param_1)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  uint uVar4;
  uint *puVar5;
  uint uStack_24;
  undefined1 auStack_20 [4];
  undefined4 uStack_1c;
  
  piVar1 = piRam10207898;
  uVar2 = func_0x10025560();
  if (*piVar1 == 0) {
    puVar5 = (uint *)(piVar1 + 4);
    for (uVar4 = 0; uVar4 < (uint)piVar1[2]; uVar4 = uVar4 + 1) {
      (*(code *)(*puVar5 & 0xfffffffe))(puVar5[1]);
      puVar5 = puVar5 + 2;
    }
    func_0x1002556c(uVar2);
    gx8002_audio_input_suspend();
    do {
      iVar3 = gx8002_snpu_get_state();
    } while (iVar3 == 1);
    gx_snpu_exit();
    auStack_20[0] = 1;
    uStack_1c = uRam1020789c;
    uStack_24 = param_1;
    func_0x10025d74(3,&uStack_24);
    func_0x10025d74(5,auStack_20);
    func_0x10025534();
    if ((uStack_24 & 4) != 0) {
      gx_audio_in_set_interrupt_enable(0x10000,1);
    }
    gx8002_printf(uRam102078a0);
    func_0x100248cc();
    uVar2 = 0;
  }
  else {
    func_0x1002556c();
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

