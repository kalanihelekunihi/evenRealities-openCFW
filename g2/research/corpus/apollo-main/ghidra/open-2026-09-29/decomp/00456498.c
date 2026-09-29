
void FUN_00456498(uint param_1)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  if (*DAT_00456578 < param_1) {
    param_1 = *DAT_00456578;
  }
  disableIRQinterrupts();
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  iVar3 = FUN_00455648();
  if (iVar3 == 0) {
    enableIRQinterrupts();
  }
  else {
    uVar4 = FUN_0048d654();
    puVar2 = DAT_00456570;
    puVar1 = DAT_0045656c;
    if (uVar4 < *DAT_0045656c) {
      iVar3 = -1 - *DAT_0045656c;
    }
    else {
      iVar3 = -*DAT_0045656c;
    }
    FUN_0048d670(0,param_1 * *DAT_00456570 - (uVar4 + iVar3));
    iVar3 = am_freertos_sleep(param_1);
    if (iVar3 != 0) {
      DataSynchronizationBarrier(0xf);
      WaitForInterrupt();
      InstructionSynchronizationBarrier(0xf);
    }
    am_freertos_wakeup(param_1);
    uVar4 = FUN_0048d654();
    if (uVar4 < *puVar1) {
      iVar3 = -1 - *puVar1;
    }
    else {
      iVar3 = -*puVar1;
    }
    uVar6 = uVar4 + iVar3;
    uVar5 = *puVar2;
    iVar3 = uVar6 - *puVar2 * (uVar6 / *puVar2);
    *puVar1 = uVar4 - iVar3;
    FUN_0048d6e6(1);
    FUN_00456374(0x20);
    FUN_0048d670(0,*puVar2 - iVar3);
    uVar4 = uVar6 / uVar5;
    if (param_1 < uVar6 / uVar5) {
      uVar4 = param_1;
    }
    FUN_00454fd8(uVar4);
    enableIRQinterrupts();
  }
  return;
}

