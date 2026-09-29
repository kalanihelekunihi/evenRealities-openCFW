
int dmConnCcbByHandle(short param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  
  cVar2 = '\x03';
  iVar1 = DAT_004b6520;
  while( true ) {
    if (cVar2 == '\0') {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67d0,&DAT_004b616c,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67d0,DAT_004b67d0,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67d0,DAT_004b67cc,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b6320,&DAT_004b6168,3), iVar1 != 0))
              {
                WsfTrace(DAT_004b67d0,DAT_004b6c60,param_1);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(4,&DAT_004b6320,DAT_004b652c,DAT_004b6c24,0xef,DAT_004b6c60,param_1);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,&DAT_004b6320,DAT_004b652c,DAT_004b6c24,0xef,DAT_004b6c60,param_1);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,&DAT_004b6320,DAT_004b652c,DAT_004b6c24,0xef,DAT_004b6c60,param_1);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,&DAT_004b6320,DAT_004b652c,DAT_004b6c24,0xef,DAT_004b6c60,param_1,param_4);
        }
      }
      return 0;
    }
    if ((*(char *)(iVar1 + 0x16) != '\0') && (*(short *)(iVar1 + 0xc) == param_1)) break;
    cVar2 = cVar2 + -1;
    iVar1 = iVar1 + 0x30;
  }
  return iVar1;
}

