
undefined1 FUN_0043d4b0(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  byte bVar4;
  
  if (param_1 == 0) {
    if (*DAT_0043daa0 == 0) {
      FUN_0043d574(0,PTR_DAT_0043da8c,DAT_0043da88,DAT_0043dac8,0x1e1,DAT_0043daac,DAT_0043dac4,
                   DAT_0043dac8,0x1e1);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0043daa0)(DAT_0043dac4,DAT_0043dac8,0x1e1);
  }
  iVar1 = DAT_0043da70;
  uVar3 = 5;
  if (*(char *)(DAT_0043da70 + 0xf0) == '\0') {
    uVar3 = 5;
  }
  else {
    FUN_0043d416();
    for (bVar4 = 0; bVar4 < 5; bVar4 = bVar4 + 1) {
      if ((*(char *)(iVar1 + (uint)bVar4 * 0x21 + 0x51) == '\x01') &&
         (iVar2 = FUN_0044b610(param_1,iVar1 + (uint)bVar4 * 0x21 + 0x32,0x1e), iVar2 == 0)) {
        uVar3 = *(undefined1 *)(iVar1 + (uint)bVar4 * 0x21 + 0x31);
        break;
      }
    }
    FUN_0043d438();
  }
  return uVar3;
}

