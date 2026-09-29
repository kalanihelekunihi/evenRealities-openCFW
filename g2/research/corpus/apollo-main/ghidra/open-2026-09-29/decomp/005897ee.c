
undefined8 FUN_005897ee(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x11e;
      param_3 = DAT_00589988;
      FUN_0043d574(2,DAT_00589944,DAT_00589940,DAT_0058998c,0x11e,DAT_00589988,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00589990);
    }
  }
  else {
    uVar2 = FUN_0044ddea(param_1);
    for (uVar5 = 0; uVar5 < uVar2; uVar5 = uVar5 + 1) {
      iVar1 = FUN_0044dce2(param_1,uVar5);
      if (iVar1 != 0) {
        iVar4 = FUN_0043e2d4(iVar1,DAT_00589998);
        if (iVar4 == 0) {
          iVar4 = FUN_0043e2d4(iVar1,DAT_00589994);
          if (iVar4 == 0) {
            FUN_005897ee(iVar1);
          }
          else {
            uVar3 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar1,uVar3,0);
          }
        }
        else {
          FUN_004413ce(iVar1,0xff,0);
        }
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

