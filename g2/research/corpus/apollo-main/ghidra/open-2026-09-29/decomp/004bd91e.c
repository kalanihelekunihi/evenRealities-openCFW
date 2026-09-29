
undefined8 FUN_004bd91e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bdb20,&DAT_004bda24,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bdb20,DAT_004bdb2c,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004bdb20,DAT_004bdb20,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004bda28,&DAT_004bda2c,3), iVar1 != 0)) {
            WsfTrace(DAT_004bdb20,DAT_004bdb30,param_1);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar2 = 0xca;
            param_2 = DAT_004bdb30;
            FUN_0043d574(4,&DAT_004bda28,DAT_004bda50,DAT_004bdb34,0xca,DAT_004bdb30,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0xca;
          param_2 = DAT_004bdb30;
          FUN_0043d574(3,&DAT_004bda28,DAT_004bda50,DAT_004bdb34,0xca,DAT_004bdb30,param_1);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0xca;
        param_2 = DAT_004bdb30;
        FUN_0043d574(2,&DAT_004bda28,DAT_004bda50,DAT_004bdb34,0xca,DAT_004bdb30,param_1);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0xca;
      param_2 = DAT_004bdb30;
      FUN_0043d574(1,&DAT_004bda28,DAT_004bda50,DAT_004bdb34,0xca,DAT_004bdb30,param_1,param_4);
    }
  }
  if (*(int *)(DAT_004bdb1c + 4) != 0) {
    (**(code **)(DAT_004bdb1c + 4))(0x10,param_1);
  }
  return CONCAT44(param_2,uVar2);
}

