
int dmConnCmplStates(void)

{
  int iVar1;
  char cVar2;
  undefined4 in_r3;
  int iVar3;
  
  cVar2 = '\x03';
  iVar3 = DAT_004b6520;
  while( true ) {
    if (cVar2 == '\0') {
      return 0;
    }
    if ((*(char *)(iVar3 + 0x16) != '\0') &&
       ((*(char *)(iVar3 + 0x15) == '\x02' ||
        ((*(char *)(iVar3 + 0x15) == '\x04' && (*(short *)(iVar3 + 0xc) == -1)))))) break;
    cVar2 = cVar2 + -1;
    iVar3 = iVar3 + 0x30;
  }
  iVar1 = FUN_004c9c50();
  if ((iVar1 != 0) && (iVar1 = FUN_0044b610(DAT_004b67cc,&DAT_004b5de0,3), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1e) {
      return iVar3;
    }
    FUN_0043d574(1,&DAT_004b5de4,DAT_004b652c,DAT_004b6528,0x9b,DAT_004b6524,
                 *(undefined1 *)(iVar3 + 0x10),in_r3);
    return iVar3;
  }
  iVar1 = FUN_004c9c50();
  if ((iVar1 != 0) && (iVar1 = FUN_0044b610(DAT_004b67cc,DAT_004b67d0,4), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1e) {
      return iVar3;
    }
    FUN_0043d574(2,&DAT_004b5de4,DAT_004b652c,DAT_004b6528,0x9b,DAT_004b6524,
                 *(undefined1 *)(iVar3 + 0x10));
    return iVar3;
  }
  iVar1 = FUN_004c9c50();
  if ((iVar1 != 0) && (iVar1 = FUN_0044b610(DAT_004b67cc,DAT_004b67cc,4), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1e) {
      return iVar3;
    }
    FUN_0043d574(3,&DAT_004b5de4,DAT_004b652c,DAT_004b6528,0x9b,DAT_004b6524,
                 *(undefined1 *)(iVar3 + 0x10));
    return iVar3;
  }
  iVar1 = FUN_004c9c50();
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1e) {
      return iVar3;
    }
    FUN_0043d574(4,&DAT_004b5de4,DAT_004b652c,DAT_004b6528,0x9b,DAT_004b6524,
                 *(undefined1 *)(iVar3 + 0x10));
    return iVar3;
  }
  iVar1 = FUN_004c9c50();
  if ((iVar1 != 0) && (iVar1 = FUN_0044b610(&DAT_004b5de4,&DAT_004b5eec,3), iVar1 == 0)) {
    return iVar3;
  }
  WsfTrace(DAT_004b67cc,DAT_004b6524,*(undefined1 *)(iVar3 + 0x10));
  return iVar3;
}

