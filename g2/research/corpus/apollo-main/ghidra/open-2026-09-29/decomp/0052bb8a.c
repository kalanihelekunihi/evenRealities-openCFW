
undefined8 attsCccAllocTbl(byte param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_0052c674;
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
              WsfTrace(DAT_0052c678,DAT_0052c67c,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x67;
              FUN_0043d574(4,&DAT_0052be2c,DAT_0052c684,DAT_0052c680,0x67,DAT_0052c67c,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x67;
            FUN_0043d574(3,&DAT_0052be2c,DAT_0052c684,DAT_0052c680,0x67,DAT_0052c67c,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x67;
          FUN_0043d574(2,&DAT_0052be2c,DAT_0052c684,DAT_0052c680,0x67,DAT_0052c67c,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x67;
        FUN_0043d574(1,&DAT_0052be2c,DAT_0052c684,DAT_0052c680,0x67,DAT_0052c67c,0);
      }
    }
    uVar2 = 0;
  }
  else {
    if (*(int *)(DAT_0052c674 + (uint)param_1 * 4 + -4) == 0) {
      uVar2 = WsfBufAlloc((uint)*(byte *)(DAT_0052c674 + 0x14) << 1);
      *(undefined4 *)(iVar1 + (uint)param_1 * 4 + -4) = uVar2;
    }
    uVar2 = *(undefined4 *)(iVar1 + (uint)param_1 * 4 + -4);
  }
  return CONCAT44(param_2,uVar2);
}

