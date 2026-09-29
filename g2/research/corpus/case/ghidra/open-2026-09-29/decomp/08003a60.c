
void right_glasses_state_reset(void)

{
  int iVar1;
  
  iVar1 = DAT_08003a80;
  *(undefined1 *)(DAT_08003a80 + 0xc) = 0;
  *(undefined1 *)(iVar1 + 0xd) = 0;
  *(undefined2 *)(iVar1 + 0x14) = 0;
  *(undefined1 *)(iVar1 + 0xe) = 0;
  *(undefined1 *)(iVar1 + 0xf) = 0;
  *(undefined2 *)(iVar1 + 0x12) = 0;
  *(undefined1 *)(iVar1 + 0x10) = 0;
  *(undefined4 *)(iVar1 + 0x1c) = 0;
  *(undefined4 *)(iVar1 + 0x18) = 0;
  *(undefined4 *)(iVar1 + 0x20) = 0;
  *(undefined4 *)(iVar1 + 0x24) = 0;
  return;
}

