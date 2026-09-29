
undefined4 FUN_0043f66c(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  
  iVar1 = DAT_0043ff90;
  if (*(char *)(DAT_0043ff90 + 0x60) == '\0') {
    *(undefined1 *)(DAT_0043ff90 + 0x60) = 1;
    iVar2 = FUN_0044dbc4();
    while ((*(ushort *)(iVar2 + 0x2a) & 7) >> 2 != 0) {
      *(ushort *)(iVar2 + 0x2a) = *(ushort *)(iVar2 + 0x2a) & 0xfffb;
      FUN_00440d70(iVar2);
    }
    *(undefined1 *)(iVar1 + 0x60) = 0;
  }
  return in_r3;
}

