
undefined8 attsCccFreeTbl(byte param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = DAT_0052c674;
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,&DAT_0052c0a0,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c678,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052c678,DAT_0052c688,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052c0a4,&LAB_0052c0a8,3), iVar1 != 0)) {
              WsfTrace(DAT_0052c678,DAT_0052c694,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0x9a;
              param_3 = DAT_0052c694;
              FUN_0043d574(4,&DAT_0052c0a4,DAT_0052c684,DAT_0052c698,0x9a,DAT_0052c694,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0x9a;
            param_3 = DAT_0052c694;
            FUN_0043d574(3,&DAT_0052c0a4,DAT_0052c684,DAT_0052c698,0x9a,DAT_0052c694,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x9a;
          param_3 = DAT_0052c694;
          FUN_0043d574(2,&DAT_0052c0a4,DAT_0052c684,DAT_0052c698,0x9a,DAT_0052c694,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x9a;
        param_3 = DAT_0052c694;
        FUN_0043d574(1,&DAT_0052c0a4,DAT_0052c684,DAT_0052c698,0x9a,DAT_0052c694,0);
      }
    }
  }
  else if (*(int *)(DAT_0052c674 + (uint)param_1 * 4 + -4) != 0) {
    WsfBufFree(*(undefined4 *)(DAT_0052c674 + (uint)param_1 * 4 + -4));
    *(undefined4 *)(iVar1 + (uint)param_1 * 4 + -4) = 0;
  }
  return CONCAT44(param_3,param_2);
}

