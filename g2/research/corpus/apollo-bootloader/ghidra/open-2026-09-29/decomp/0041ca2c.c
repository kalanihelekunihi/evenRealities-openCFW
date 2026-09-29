
bool FUN_0041ca2c(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5)

{
  int iVar1;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_18 = param_1;
  local_14 = param_3;
  local_10 = param_4;
  uStack_c = param_5;
  iVar1 = FUN_0041cd1a(2,0,&local_18);
  if (iVar1 != 0) {
    *param_2 = 0;
    param_2[1] = 0;
  }
  else {
    *param_2 = local_14;
    param_2[1] = local_10;
  }
  return iVar1 != 0;
}

