
void FUN_004b3c02(void)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = DAT_004b3c8c;
  FUN_0043c0e4(DAT_004b3c8c,0x80,0);
  for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
    *(undefined1 *)((uint)bVar2 + iVar1 + 0x57) = 3;
    *(undefined1 *)((uint)bVar2 + iVar1 + 0x59) = 0;
    *(undefined1 *)((uint)bVar2 + iVar1 + 0x5b) = 0;
    *(undefined1 *)((uint)bVar2 + iVar1 + 0x6a) = 0;
    FUN_0043c0e4(iVar1 + (uint)bVar2 * 6 + 0x5e,6,0);
  }
  *(undefined1 *)(iVar1 + 0x5d) = 0xff;
  FUN_004b32d4();
  *(undefined1 *)(iVar1 + 0x74) = 0;
  FUN_00479418();
  *DAT_004b46ec = DAT_004b46a4;
  return;
}

