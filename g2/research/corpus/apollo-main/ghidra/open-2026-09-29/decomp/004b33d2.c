
void FUN_004b33d2(byte param_1,char param_2)

{
  int iVar1;
  
  iVar1 = DAT_004b3c8c;
  *(undefined2 *)(DAT_004b3c8c + (uint)param_1 * 8 + (uint)(byte)(param_2 << 1) * 2 + 0x40) = 0;
  *(undefined2 *)(iVar1 + (uint)param_1 * 8 + (uint)(byte)(param_2 * '\x02' + 1) * 2 + 0x40) = 0;
  *(undefined1 *)((uint)param_1 + iVar1 + 0x55) = 0;
  return;
}

