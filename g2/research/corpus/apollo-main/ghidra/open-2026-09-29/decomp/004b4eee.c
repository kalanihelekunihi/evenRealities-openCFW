
int attCcbByConnId(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b51d4,&DAT_004b5010,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b51d4,DAT_004b51d4,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b51d4,DAT_004b51dc,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&LAB_004b5038,&LAB_004b50ec,3), iVar1 != 0)) {
              WsfTrace(DAT_004b51d4,DAT_004b51e0,0);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&LAB_004b5038,DAT_004b51d8,DAT_004b51e4,0x13f,DAT_004b51e0,0);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&LAB_004b5038,DAT_004b51d8,DAT_004b51e4,0x13f,DAT_004b51e0,0);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&LAB_004b5038,DAT_004b51d8,DAT_004b51e4,0x13f,DAT_004b51e0,0);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&LAB_004b5038,DAT_004b51d8,DAT_004b51e4,0x13f,DAT_004b51e0,0,param_4);
      }
    }
    iVar1 = 0;
  }
  else {
    iVar1 = DAT_004b51d0 + (uint)param_1 * 0x14 + -0x14;
  }
  return iVar1;
}

