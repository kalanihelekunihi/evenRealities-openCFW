
bool FUN_0055e90c(byte param_1)

{
  int iVar1;
  
  iVar1 = DAT_0055e98c;
  if (param_1 < 4) {
    *(undefined4 *)(*(int *)((uint)param_1 * 0x1c + DAT_0055e98c + 0x10) + 8) = 0;
    FUN_0043bb00(*(undefined4 *)(*(int *)((uint)param_1 * 0x1c + iVar1 + 0x10) + 0xc),0,0x400);
    FUN_0058e352(*(undefined4 *)(iVar1 + (uint)param_1 * 0x1c + 4));
  }
  return param_1 >= 4;
}

