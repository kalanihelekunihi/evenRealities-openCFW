
undefined8
FUN_00567e24(undefined4 *param_1,undefined4 *param_2,undefined4 *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  undefined4 *local_18;
  undefined4 uStack_14;
  
  uVar1 = *param_1;
  *param_3 = 0;
  local_18 = param_3;
  uStack_14 = param_4;
  puVar2 = (undefined4 *)ft_mem_alloc(uVar1,*param_2,&local_18);
  if (local_18 == (undefined4 *)0x0) {
    *puVar2 = param_1;
    puVar2[1] = param_2;
    puVar2[2] = param_2[1];
    *param_3 = puVar2;
  }
  return CONCAT44(local_18,local_18);
}

