
undefined1 FUN_00410af2(int *param_1,int *param_2)

{
  undefined1 uVar1;
  
  if ((((*param_1 == *param_2) || (param_1[1] == param_2[1])) || (*param_1 == param_2[1])) ||
     (param_1[1] == *param_2)) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

