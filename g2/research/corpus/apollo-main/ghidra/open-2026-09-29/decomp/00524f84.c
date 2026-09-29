
undefined4 ft_validator_run(int param_1,undefined4 param_2)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_1 + 0x8c) = param_2;
  FUN_00567790(param_1,1);
  return unaff_r7;
}

