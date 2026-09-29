
undefined4 FUN_0800cb38(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_0800cb98;
  uVar4 = 0;
  if (param_1 != 0) {
    if (param_1 != *DAT_0800cb98) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if (*(int *)(param_1 + 0x50) == 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    iVar2 = *(int *)(param_1 + 0x50) + -1;
    *(int *)(param_1 + 0x50) = iVar2;
    if ((*(int *)(param_1 + 0x2c) != *(int *)(param_1 + 0x4c)) && (iVar2 == 0)) {
      uxListRemove(param_1 + 4);
      *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x4c);
      *(int *)(param_1 + 0x18) = 0x38 - *(int *)(param_1 + 0x4c);
      uVar3 = *(uint *)(param_1 + 0x2c);
      if ((uint)piVar1[4] < uVar3) {
        piVar1[4] = uVar3;
      }
      FUN_0800bfe2(uVar3 * 0x14 + DAT_0800cb9c,param_1 + 4);
      uVar4 = 1;
    }
  }
  return uVar4;
}

