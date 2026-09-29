
undefined4 FUN_0800cc0c(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  piVar1 = DAT_0800ccb4;
  iVar5 = 0;
  uVar6 = 0;
  if (DAT_0800ccb4[0xc] != 0) {
    FUN_0800bffc();
    piVar1[0xc] = piVar1[0xc] + -1;
    piVar2 = DAT_0800ccb8;
    if ((piVar1[0xc] == 0) && (piVar1[2] != 0)) {
      iVar3 = *DAT_0800ccb8;
      while (iVar3 != 0) {
        iVar5 = *(int *)(piVar2[3] + 0xc);
        uxListRemove(iVar5 + 0x18);
        uxListRemove(iVar5 + 4);
        uVar4 = *(uint *)(iVar5 + 0x2c);
        if ((uint)piVar1[4] < uVar4) {
          piVar1[4] = uVar4;
        }
        FUN_0800bfe2(uVar4 * 0x14 + DAT_0800ccbc,iVar5 + 4);
        if (*(uint *)(*piVar1 + 0x2c) <= *(uint *)(iVar5 + 0x2c)) {
          piVar1[7] = 1;
        }
        iVar3 = *piVar2;
      }
      if (iVar5 != 0) {
        FUN_0800b260();
      }
      iVar5 = piVar1[6];
      if (iVar5 != 0) {
        do {
          iVar3 = xTaskIncrementTick();
          if (iVar3 != 0) {
            piVar1[7] = 1;
          }
          iVar5 = iVar5 + -1;
        } while (iVar5 != 0);
        piVar1[6] = 0;
      }
      if (piVar1[7] != 0) {
        uVar6 = 1;
        FUN_0800c0a0();
      }
    }
    FUN_0800c014();
    return uVar6;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

