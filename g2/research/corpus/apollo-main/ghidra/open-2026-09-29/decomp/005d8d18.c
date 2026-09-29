
undefined8 FUN_005d8d18(int *param_1,undefined4 param_2,int *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int *local_10;
  undefined4 uStack_c;
  
  uVar1 = 0;
  if (*param_1 == 0) {
    local_10 = param_3;
    uStack_c = param_4;
    uVar1 = FUN_005d8cde(param_1,param_2,&local_10);
  }
  else {
    local_10 = (int *)(param_1[2] + *param_1 * 0x10 + -0x10);
  }
  *param_3 = (int)local_10;
  return CONCAT44(local_10,uVar1);
}

