
undefined4 FUN_00505f10(int param_1,undefined4 param_2)

{
  undefined4 unaff_r7;
  
  if (*(int *)(param_1 + 0xc) != 0) {
    (**(code **)(param_1 + 0xc))(param_2);
  }
  return unaff_r7;
}

