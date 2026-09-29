
void FUN_0041b754(uint param_1)

{
  uint *puVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  if (*DAT_0041b834 < param_1) {
    param_1 = *DAT_0041b834;
  }
  disableIRQinterrupts();
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  iVar3 = FUN_00418a00();
  if (iVar3 == 0) {
    enableIRQinterrupts();
  }
  else {
    uVar4 = FUN_0041f424();
    puVar2 = DAT_0041b82c;
    puVar1 = DAT_0041b828;
    if (uVar4 < *DAT_0041b828) {
      iVar3 = -1 - *DAT_0041b828;
    }
    else {
      iVar3 = -*DAT_0041b828;
    }
    FUN_0041f440(0,param_1 * *DAT_0041b82c - (uVar4 + iVar3));
    iVar3 = FUN_0041b5e8(param_1);
    if (iVar3 != 0) {
      DataSynchronizationBarrier(0xf);
      WaitForInterrupt();
      InstructionSynchronizationBarrier(0xf);
    }
    FUN_0041b5f4(param_1);
    uVar4 = FUN_0041f424();
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
    FUN_0041f4b6(1);
    FUN_0041b630(0x20);
    FUN_0041f440(0,*puVar2 - iVar3);
    uVar4 = uVar6 / uVar5;
    if (param_1 < uVar6 / uVar5) {
      uVar4 = param_1;
    }
    FUN_00418394(uVar4);
    enableIRQinterrupts();
  }
  return;
}

