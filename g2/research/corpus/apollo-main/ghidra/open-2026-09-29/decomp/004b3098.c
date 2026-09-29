
void dmAdvCbInit(byte param_1)

{
  int iVar1;
  
  iVar1 = DAT_004b32cc;
  *(undefined1 *)((uint)param_1 + DAT_004b32cc + 0x18) = 0xff;
  *(undefined2 *)(iVar1 + (uint)param_1 * 2 + 0x10) = 0x640;
  *(undefined2 *)(iVar1 + (uint)param_1 * 2 + 0x14) = 0x780;
  *(undefined1 *)((uint)param_1 + iVar1 + 0x1a) = 7;
  *(undefined1 *)(DAT_004b32d0 + (uint)param_1 + 0x11) = 0;
  *(undefined1 *)((uint)param_1 + iVar1 + 0x1d) = 0;
  return;
}

