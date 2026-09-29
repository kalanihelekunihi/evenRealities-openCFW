
undefined8 dmConnCcbByBdAddr(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  char cVar3;
  
  iVar2 = DAT_004b6520;
  for (cVar3 = '\x03'; cVar3 != '\0'; cVar3 = cVar3 + -1) {
    if ((*(char *)(iVar2 + 0x16) != '\0') && (iVar1 = FUN_004d294a(iVar2,param_1), iVar1 != 0))
    goto LAB_004b62a6;
    iVar2 = iVar2 + 0x30;
  }
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,&LAB_004b6484,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,DAT_004b67d0,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_004b67cc,DAT_004b67cc,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b6320,&DAT_004b651c,3), iVar2 != 0)) {
            WsfTrace(DAT_004b67cc,DAT_004b6dcc);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_3 = 0x10a;
            FUN_0043d574(4,&DAT_004b6320,DAT_004b652c,DAT_004b6dd0,0x10a,DAT_004b6dcc);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_3 = 0x10a;
          FUN_0043d574(3,&DAT_004b6320,DAT_004b652c,DAT_004b6dd0,0x10a,DAT_004b6dcc);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x10a;
        FUN_0043d574(2,&DAT_004b6320,DAT_004b652c,DAT_004b6dd0,0x10a,DAT_004b6dcc);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x10a;
      FUN_0043d574(1,&DAT_004b6320,DAT_004b652c,DAT_004b6dd0,0x10a,DAT_004b6dcc);
    }
  }
  iVar2 = 0;
LAB_004b62a6:
  return CONCAT44(param_3,iVar2);
}

