
undefined1 FUN_0041760a(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  byte bVar4;
  
  if (param_1 == 0) {
    if (*DAT_00417be8 == 0) {
      elog_output(0,DAT_00417be4,DAT_00417be0,DAT_00417c0c,0x1e1,DAT_00417bf4,DAT_00417c08,
                  DAT_00417c0c,0x1e1);
      do {
        FUN_0041ac8a();
      } while( true );
    }
    (*(code *)*DAT_00417be8)(DAT_00417c08,DAT_00417c0c,0x1e1);
  }
  iVar1 = DAT_00417bcc;
  uVar3 = 5;
  if (*(char *)(DAT_00417bcc + 0xf0) == '\0') {
    uVar3 = 5;
  }
  else {
    FUN_00417570();
    for (bVar4 = 0; bVar4 < 5; bVar4 = bVar4 + 1) {
      if ((*(char *)(iVar1 + (uint)bVar4 * 0x21 + 0x51) == '\x01') &&
         (iVar2 = FUN_0041b0f4(param_1,iVar1 + (uint)bVar4 * 0x21 + 0x32,0x1e), iVar2 == 0)) {
        uVar3 = *(undefined1 *)(iVar1 + (uint)bVar4 * 0x21 + 0x31);
        break;
      }
    }
    FUN_00417592();
  }
  return uVar3;
}

