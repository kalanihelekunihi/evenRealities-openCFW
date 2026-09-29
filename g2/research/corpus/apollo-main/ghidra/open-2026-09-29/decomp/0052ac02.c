
void HciCoreInit(void)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = DAT_0052ae14;
  *(undefined4 *)(DAT_0052ae14 + 0x70) = 0;
  *(undefined4 *)(iVar1 + 0x74) = 0;
  for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
    *(undefined2 *)(iVar1 + (uint)bVar2 * 0x1c + 0x10) = 0xffff;
  }
  for (bVar2 = 0; bVar2 < 6; bVar2 = bVar2 + 1) {
    *(undefined2 *)(iVar1 + (uint)bVar2 * 2 + 0x54) = 0xffff;
  }
  *(undefined2 *)(iVar1 + 0x7c) = 0x1b;
  *(undefined1 *)(iVar1 + 0x80) = 0xe;
  *(undefined1 *)(iVar1 + 0x81) = 0xd;
  *(undefined4 *)(iVar1 + 0xa0) = 0;
  hciCoreInit();
  return;
}

