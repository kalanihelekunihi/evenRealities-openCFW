
void FUN_004175b4(void)

{
  int iVar1;
  byte bVar2;
  
  for (bVar2 = 0; iVar1 = DAT_00417bcc, bVar2 < 5; bVar2 = bVar2 + 1) {
    FUN_0041560c(DAT_00417bcc + (uint)bVar2 * 0x21 + 0x32,0x1f,0);
    *(undefined1 *)(iVar1 + (uint)bVar2 * 0x21 + 0x31) = 0;
    *(undefined1 *)(iVar1 + (uint)bVar2 * 0x21 + 0x51) = 0;
  }
  return;
}

