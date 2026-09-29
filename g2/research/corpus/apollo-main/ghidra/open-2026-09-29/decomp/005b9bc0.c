
void FUN_005b9bc0(int *param_1)

{
  int iVar1;
  undefined1 auStack_2c [32];
  
  if (param_1 != (int *)0x0) {
    if ((*param_1 != 0) && (iVar1 = FUN_0043e2ea(*param_1), iVar1 == 1)) {
      FUN_005b8d20(param_1);
    }
    if ((param_1[1] != 0) && (iVar1 = FUN_0043e2ea(param_1[1]), iVar1 == 1)) {
      FUN_0043c0e4(auStack_2c,0x20,0);
      FUN_005b8bc8((char)param_1[2],auStack_2c,0x20);
      FUN_0049942e(param_1[1],auStack_2c);
      if ((*param_1 != 0) && (iVar1 = FUN_0043e2ea(*param_1), iVar1 == 1)) {
        FUN_0043f6d6(param_1[1],*param_1,0x14,8,0);
      }
    }
  }
  return;
}

