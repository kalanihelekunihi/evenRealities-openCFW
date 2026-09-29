
void FUN_0054ff64(int param_1,int param_2,undefined1 param_3,byte param_4)

{
  int iVar1;
  
  iVar1 = DAT_00550948;
  if (((param_1 != 0) && (param_2 != 0)) && (param_4 < 10)) {
    *(int *)(DAT_00550948 + (uint)param_4 * 0xc) = param_1;
    *(int *)((uint)param_4 * 0xc + iVar1 + 4) = param_2;
    *(undefined1 *)((uint)param_4 * 0xc + iVar1 + 8) = param_3;
    *(byte *)((uint)param_4 * 0xc + iVar1 + 9) = param_4;
    *(undefined1 *)(iVar1 + (uint)param_4 * 0xc + 10) = 1;
  }
  return;
}

