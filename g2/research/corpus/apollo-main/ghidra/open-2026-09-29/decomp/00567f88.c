
undefined4
FUN_00567f88(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    uVar1 = *(undefined4 *)*param_1;
    if (*(int *)(param_1[1] + 0xc) != 0) {
      (**(code **)(param_1[1] + 0xc))(param_1);
    }
    ft_mem_free(uVar1,param_1);
  }
  return param_4;
}

