
undefined8 dmConnCcbDealloc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b6ba8,&DAT_004b6014,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b6ba8,DAT_004b67d0,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b6ba8,DAT_004b67cc,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&LAB_004b6018,&DAT_004b6168,3), iVar1 != 0)) {
            WsfTrace(DAT_004b6ba8,DAT_004b6ab0,*(undefined1 *)(param_1 + 0x10));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0xd4;
            param_2 = DAT_004b6ab0;
            FUN_0043d574(4,&LAB_004b6018,DAT_004b652c,DAT_004b6ab4,0xd4,DAT_004b6ab0,
                         *(undefined1 *)(param_1 + 0x10));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0xd4;
          param_2 = DAT_004b6ab0;
          FUN_0043d574(3,&LAB_004b6018,DAT_004b652c,DAT_004b6ab4,0xd4,DAT_004b6ab0,
                       *(undefined1 *)(param_1 + 0x10));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar2 = 0xd4;
        param_2 = DAT_004b6ab0;
        FUN_0043d574(2,&LAB_004b6018,DAT_004b652c,DAT_004b6ab4,0xd4,DAT_004b6ab0,
                     *(undefined1 *)(param_1 + 0x10));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0xd4;
      param_2 = DAT_004b6ab0;
      FUN_0043d574(1,&LAB_004b6018,DAT_004b652c,DAT_004b6ab4,0xd4,DAT_004b6ab0,
                   *(undefined1 *)(param_1 + 0x10),param_4);
    }
  }
  *(undefined1 *)(param_1 + 0x16) = 0;
  return CONCAT44(param_2,iVar2);
}

