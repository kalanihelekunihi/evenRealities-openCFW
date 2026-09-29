
undefined8 FUN_005e2224(undefined4 param_1,undefined4 *param_2,undefined4 param_3,int param_4)

{
  undefined4 *puVar1;
  int local_10;
  
  *param_2 = 0;
  local_10 = param_4;
  puVar1 = (undefined4 *)ft_mem_alloc(param_1,4,&local_10);
  if (local_10 == 0) {
    *puVar1 = param_1;
    *param_2 = puVar1;
  }
  return CONCAT44(local_10,local_10);
}

