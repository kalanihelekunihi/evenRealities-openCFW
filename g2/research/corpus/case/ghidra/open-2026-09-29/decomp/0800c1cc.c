
void FUN_0800c1cc(uint *param_1,uint param_2)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  
  piVar1 = DAT_0800c220;
  if (DAT_0800c220[0xc] == 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  *param_1 = param_2 | 0x80000000;
  uVar3 = param_1[3];
  if (uVar3 != 0) {
    uxListRemove();
    uxListRemove(uVar3 + 4);
    uVar2 = *(uint *)(uVar3 + 0x2c);
    if ((uint)piVar1[4] < uVar2) {
      piVar1[4] = uVar2;
    }
    FUN_0800bfe2(uVar2 * 0x14 + DAT_0800c224,uVar3 + 4);
    if (*(uint *)(*piVar1 + 0x2c) < *(uint *)(uVar3 + 0x2c)) {
      piVar1[7] = 1;
    }
    return;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

