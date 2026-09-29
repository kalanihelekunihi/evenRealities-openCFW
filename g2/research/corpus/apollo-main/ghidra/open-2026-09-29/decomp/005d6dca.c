
undefined8 FUN_005d6dca(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int local_18;
  
  local_18 = 0;
  puVar1 = (undefined4 *)ft_mem_alloc(param_1,0x14,&local_18,param_4,param_2,param_3);
  if (local_18 == 0) {
    *puVar1 = param_1;
    puVar1[1] = param_2;
  }
  uVar3 = 0;
  uVar2 = ft_mem_realloc(param_1,8,0,param_3,0,&local_18);
  puVar1[2] = uVar2;
  if (local_18 == 0) {
    puVar1[4] = param_3;
    puVar1[3] = puVar1[2];
  }
  else {
    ft_mem_free(param_1,puVar1);
    puVar1 = (undefined4 *)0x0;
  }
  return CONCAT44(uVar3,puVar1);
}

