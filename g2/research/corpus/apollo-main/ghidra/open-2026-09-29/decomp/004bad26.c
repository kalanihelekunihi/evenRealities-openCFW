
undefined1 FUN_004bad26(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004bb3a0,&LAB_004bae68,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a0,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004bb3a0,DAT_004bb3a8,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004bae7c,&LAB_004bae80,3), iVar2 != 0)) {
              WsfTrace(DAT_004bb3a0,DAT_004bb3b0,0);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_004bae7c,DAT_004bb3a4,DAT_004bb3b4,0xb5,DAT_004bb3b0,0);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_004bae7c,DAT_004bb3a4,DAT_004bb3b4,0xb5,DAT_004bb3b0,0);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_004bae7c,DAT_004bb3a4,DAT_004bb3b4,0xb5,DAT_004bb3b0,0);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_004bae7c,DAT_004bb3a4,DAT_004bb3b4,0xb5,DAT_004bb3b0,0,param_4);
      }
    }
    uVar1 = 0;
  }
  else {
    uVar1 = *(undefined1 *)(DAT_004bb3ac + (uint)param_1 * 0x30 + -0x2b);
  }
  return uVar1;
}

