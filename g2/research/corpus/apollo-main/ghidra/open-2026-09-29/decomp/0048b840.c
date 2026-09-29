
undefined8 FUN_0048b840(int *param_1,undefined4 param_2,undefined1 param_3)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if (*param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (*(code *)*param_1)(param_2,param_3);
  }
  return CONCAT44(unaff_r7,uVar1);
}

