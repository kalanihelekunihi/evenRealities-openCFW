
undefined8 FUN_005cfbb4(undefined4 *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  undefined4 *puVar1;
  int iVar2;
  int local_18;
  
  local_18 = param_4;
  puVar1 = (undefined4 *)ft_mem_alloc(param_2,0x10,&local_18);
  iVar2 = local_18;
  if (local_18 == 0) {
    puVar1[1] = param_3;
    *puVar1 = puVar1[1];
    puVar1[2] = param_4;
    puVar1[3] = 2;
    *param_1 = param_2;
    param_1[1] = puVar1;
    param_1[2] = 0;
    param_1[3] = 0;
    iVar2 = 0;
  }
  return CONCAT44(local_18,iVar2);
}

