
undefined4
attsCsfIsClientChangeAware(byte param_1,short param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d08c,&DAT_0052ca9c,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d08c,DAT_0052d08c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_0052d08c,DAT_0052d35c,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_0052caa0,&LAB_0052caa4,3), iVar1 != 0)) {
              WsfTrace(DAT_0052d08c,DAT_0052d4e8,0,param_2);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0052caa0,DAT_0052d088,DAT_0052d4ec,0x80,DAT_0052d4e8,0,param_2);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0052caa0,DAT_0052d088,DAT_0052d4ec,0x80,DAT_0052d4e8,0,param_2);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0052caa0,DAT_0052d088,DAT_0052d4ec,0x80,DAT_0052d4e8,0,param_2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0052caa0,DAT_0052d088,DAT_0052d4ec,0x80,DAT_0052d4e8,0,param_2,param_4);
      }
    }
    uVar2 = 0;
  }
  else if ((((int)((uint)*(byte *)(DAT_0052d07c + (uint)param_1 * 2 + -2) << 0x1f) < 0) &&
           (*(char *)(DAT_0052d07c + (uint)param_1 * 2 + -1) == '\x03')) && (param_2 != 0x12)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

