
undefined4 FUN_0800cba0(int param_1)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = *(int *)(*(int *)(param_1 + 0xc) + 0xc);
  if (iVar3 == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  uxListRemove();
  piVar1 = DAT_0800cc00;
  if (DAT_0800cc00[0xc] == 0) {
    uxListRemove(iVar3 + 4);
    uVar2 = *(uint *)(iVar3 + 0x2c);
    if ((uint)piVar1[4] < uVar2) {
      piVar1[4] = uVar2;
    }
    FUN_0800bfe2(uVar2 * 0x14 + DAT_0800cc08,iVar3 + 4);
  }
  else {
    FUN_0800bfe2(DAT_0800cc04,iVar3 + 0x18);
  }
  if (*(uint *)(*piVar1 + 0x2c) < *(uint *)(iVar3 + 0x2c)) {
    piVar1[7] = 1;
    return 1;
  }
  return 0;
}

