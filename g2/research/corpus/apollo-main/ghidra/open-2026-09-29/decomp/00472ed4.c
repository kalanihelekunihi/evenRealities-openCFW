
int FUN_00472ed4(undefined1 *param_1,undefined1 param_2,int param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if (0 < param_3) {
    while (param_3 != 0) {
      if (param_1 != (undefined1 *)0x0) {
        *param_1 = param_2;
        param_1 = param_1 + 1;
      }
      iVar1 = iVar1 + 1;
      param_3 = param_3 + -1;
    }
  }
  return iVar1;
}

