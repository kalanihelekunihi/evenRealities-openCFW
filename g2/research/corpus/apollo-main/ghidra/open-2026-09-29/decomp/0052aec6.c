
void hciCmdInit(void)

{
  int iVar1;
  
  iVar1 = DAT_0052b6b4;
  *(undefined4 *)(DAT_0052b6b4 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x14) = 0;
  *(undefined1 *)(iVar1 + 0x1a) = 1;
  *(undefined1 *)(iVar1 + 10) = 1;
  *(undefined1 *)(iVar1 + 0xc) = *(undefined1 *)(DAT_0052b6b8 + 0x20);
  return;
}

