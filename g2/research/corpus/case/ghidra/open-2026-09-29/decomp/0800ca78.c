
undefined4 xTaskIncrementTick(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_0800cb30;
  uVar5 = 0;
  if (DAT_0800cb30[0xc] == 0) {
    uVar4 = DAT_0800cb30[3] + 1;
    DAT_0800cb30[3] = uVar4;
    if (uVar4 == 0) {
      if (*(int *)piVar1[0xd] != 0) {
        disableIRQinterrupts();
        do {
                    /* WARNING: Do nothing block with infinite loop */
        } while( true );
      }
      iVar2 = piVar1[0xd];
      piVar1[0xd] = piVar1[0xe];
      piVar1[0xe] = iVar2;
      piVar1[8] = piVar1[8] + 1;
      FUN_0800b260();
    }
    if ((uint)piVar1[10] <= uVar4) {
      while (*(int *)piVar1[0xd] != 0) {
        iVar2 = *(int *)(*(int *)(piVar1[0xd] + 0xc) + 0xc);
        if (uVar4 < *(uint *)(iVar2 + 4)) {
          piVar1[10] = *(uint *)(iVar2 + 4);
          goto LAB_0800cada;
        }
        uxListRemove(iVar2 + 4);
        if (*(int *)(iVar2 + 0x28) != 0) {
          uxListRemove(iVar2 + 0x18);
        }
        uVar3 = *(uint *)(iVar2 + 0x2c);
        if ((uint)piVar1[4] < uVar3) {
          piVar1[4] = uVar3;
        }
        FUN_0800bfe2(uVar3 * 0x14 + DAT_0800cb34,iVar2 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(iVar2 + 0x2c)) {
          uVar5 = 1;
        }
      }
      piVar1[10] = -1;
    }
LAB_0800cada:
    if (1 < *(uint *)(DAT_0800cb34 + *(int *)(*piVar1 + 0x2c) * 0x14)) {
      uVar5 = 1;
    }
    if (piVar1[7] != 0) {
      uVar5 = 1;
    }
  }
  else {
    DAT_0800cb30[6] = DAT_0800cb30[6] + 1;
  }
  return uVar5;
}

