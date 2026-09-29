
void FUN_0055ba70(void)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  
  for (bVar3 = 0; iVar2 = DAT_0055bbc0, iVar1 = DAT_0055bbbc, bVar3 < 2; bVar3 = bVar3 + 1) {
    *(undefined2 *)(DAT_0055bbbc + (uint)bVar3 * 2 + 0x10) = 0x60;
    *(undefined2 *)(iVar1 + (uint)bVar3 * 2 + 0x14) = 0x30;
  }
  *(undefined1 *)(DAT_0055bbc0 + 0x13) = 0;
  iVar1 = DAT_0055bbbc;
  *(undefined1 *)(DAT_0055bbbc + 0xc) = *(undefined1 *)(iVar2 + 0xc);
  *(undefined1 *)(iVar1 + 0x18) = 0;
  *(undefined1 *)(iVar2 + 0xf) = 0;
  return;
}

