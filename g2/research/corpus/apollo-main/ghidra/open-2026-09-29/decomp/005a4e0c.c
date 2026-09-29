
undefined8 FUN_005a4e0c(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((*DAT_005a4e98 == 0) && (*DAT_005a4e9c == 0)) {
    iVar1 = FUN_0047f5b8(0x1d);
    if (iVar1 == 0) {
      iVar1 = FUN_00480028(DAT_005a4e64,&stack0xfffffff0);
      if (iVar1 == 0) {
        iVar1 = FUN_004807fc(0x9c4,DAT_005a4ef0,1,0);
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

