
undefined4 FUN_00450f00(int *param_1,int *param_2)

{
  undefined4 uVar1;
  
  if ((((param_2[2] < *param_1) || (param_1[2] < *param_2)) || (param_2[3] < param_1[1])) ||
     (param_1[3] < param_2[1])) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

