
void FUN_0800c228(int param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  piVar1 = DAT_0800c27c;
  if (param_1 != 0) {
    if (param_1 != *DAT_0800c27c) {
      FUN_0800bffc();
      iVar2 = FUN_0800b330(param_1);
      if (iVar2 != 0) {
        uxListRemove(param_1 + 4);
        uVar3 = *(uint *)(param_1 + 0x2c);
        if ((uint)piVar1[4] < uVar3) {
          piVar1[4] = uVar3;
        }
        FUN_0800bfe2(uVar3 * 0x14 + DAT_0800c280,param_1 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(param_1 + 0x2c)) {
          FUN_0800c0a0();
        }
      }
      FUN_0800c014();
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

