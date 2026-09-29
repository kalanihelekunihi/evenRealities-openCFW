
undefined4 FUN_00568844(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != 0) {
    uVar1 = **(undefined4 **)(param_1 + 0x74);
    FUN_0056868c(param_1 + 0x34);
    FUN_0056868c(param_1 + 0x54);
    *(undefined4 *)(param_1 + 0x74) = 0;
    ft_mem_free(uVar1,param_1);
  }
  return param_4;
}

