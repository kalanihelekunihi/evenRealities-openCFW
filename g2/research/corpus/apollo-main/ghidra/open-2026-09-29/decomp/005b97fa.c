
void FUN_005b97fa(int *param_1)

{
  int iVar1;
  undefined1 auStack_1c [16];
  
  if ((((param_1 != (int *)0x0) && (*param_1 != 0)) && (param_1[1] != 0)) &&
     ((iVar1 = FUN_0043e2ea(*param_1), iVar1 != 0 && (iVar1 = FUN_0043e2ea(param_1[1]), iVar1 != 0))
     )) {
    FUN_005b8d20(param_1);
    FUN_0043c0e4(auStack_1c,0x10,0);
    FUN_005b8bc8((char)param_1[2],auStack_1c,0x10);
    FUN_0049942e(param_1[1],auStack_1c);
    FUN_0043f6d6(param_1[1],*param_1,0x14,8,0);
  }
  return;
}

