
undefined8 FUN_005a1da4(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((*DAT_005a1e2c == 0) && (*DAT_005a1e30 == 0)) {
    iVar1 = FUN_0047f5b8(0x1d);
    if (iVar1 == 0) {
      iVar1 = FUN_00480028(DAT_005a1dfc,&stack0xfffffff0);
      if (iVar1 == 0) {
        iVar1 = FUN_004807fc(0x9c4,DAT_005a1e88,1,0);
        if (iVar1 == 0) {
          uVar2 = 0;
        }
        else {
          uVar2 = 4;
        }
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(unaff_r5,uVar2);
}

