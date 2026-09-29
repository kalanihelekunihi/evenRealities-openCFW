
void left_glasses_state_reset(void)

{
  int iVar1;
  
  iVar1 = DAT_08003a5c;
  *(undefined1 *)(DAT_08003a5c + 0x10) = 0;
  *(undefined1 *)(iVar1 + 0x11) = 0;
  *(undefined2 *)(iVar1 + 0x18) = 0;
  *(undefined1 *)(iVar1 + 0x12) = 0;
  *(undefined1 *)(iVar1 + 0x13) = 0;
  *(undefined2 *)(iVar1 + 0x16) = 0;
  *(undefined1 *)(iVar1 + 0x14) = 0;
  *(undefined4 *)(iVar1 + 0x20) = 0;
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  *(undefined4 *)(iVar1 + 0x28) = 0;
  return;
}

