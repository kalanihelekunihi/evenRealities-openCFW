
undefined8 FUN_00463fb0(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    if (0 < param_1[7]) {
      FUN_0043f506(*param_1,param_1[7]);
    }
    if (0 < param_1[8]) {
      FUN_0043f568(*param_1,param_1[8]);
    }
    FUN_00439be4(&local_10,param_1 + 10,3);
    FUN_0044127e(*param_1,local_10,0);
    FUN_0044129e(*param_1,*(undefined1 *)((int)param_1 + 0x2b),0);
    FUN_0043dfa4(*param_1,2);
  }
  return CONCAT44(uStack_c,local_10);
}

