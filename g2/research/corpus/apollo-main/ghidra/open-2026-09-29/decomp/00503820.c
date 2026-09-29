
undefined4 FUN_00503820(undefined2 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DmConnSecLevel((char)*param_1);
  if (iVar1 == 0) {
    if ((*(char *)(*DAT_00503ff4 + 4) == '\0') && (*(char *)(param_2 + 8) == '\0')) {
      FUN_00503498((char)*param_1,1,param_2);
    }
  }
  else {
    FUN_00503498((char)*param_1,0,param_2);
  }
  return param_4;
}

