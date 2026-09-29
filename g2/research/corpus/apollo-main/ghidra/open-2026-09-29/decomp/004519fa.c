
undefined8 FUN_004519fa(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 local_10;
  
  if (*(int *)(param_1 + 8) == 0x1b) {
    piVar1 = *(int **)(param_1 + 0x10);
    if (param_2 < *piVar1) {
      param_2 = *piVar1;
    }
    *piVar1 = param_2;
    local_10 = param_3;
  }
  else {
    local_10 = DAT_00451a54;
    FUN_0044d25c(2,DAT_00451a3c,0x11c,DAT_00451a68);
  }
  return CONCAT44(param_4,local_10);
}

