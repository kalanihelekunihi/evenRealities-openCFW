
undefined4 attsCccGetTbl(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,&DAT_0052be28,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c678,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c688,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052be2c,&LAB_0052be30,3), iVar1 != 0)) {
              WsfTrace(DAT_0052c678,DAT_0052c68c,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052be2c,DAT_0052c684,DAT_0052c690,0x85,DAT_0052c68c,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052be2c,DAT_0052c684,DAT_0052c690,0x85,DAT_0052c68c,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052be2c,DAT_0052c684,DAT_0052c690,0x85,DAT_0052c68c,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052be2c,DAT_0052c684,DAT_0052c690,0x85,DAT_0052c68c,0,param_4);
      }
    }
    uVar2 = 0;
  }
  else {
    uVar2 = *(undefined4 *)(DAT_0052c674 + (uint)param_1 * 4 + -4);
  }
  return uVar2;
}

