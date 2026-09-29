
void FUN_0043d45a(void)

{
  int iVar1;
  byte bVar2;
  
  for (bVar2 = 0; iVar1 = DAT_0043da70, bVar2 < 5; bVar2 = bVar2 + 1) {
    FUN_0043c0e4(DAT_0043da70 + (uint)bVar2 * 0x21 + 0x32,0x1f,0);
    *(undefined1 *)(iVar1 + (uint)bVar2 * 0x21 + 0x31) = 0;
    *(undefined1 *)(iVar1 + (uint)bVar2 * 0x21 + 0x51) = 0;
  }
  return;
}

