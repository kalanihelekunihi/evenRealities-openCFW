
undefined8 FUN_005687b6(undefined4 *param_1,int *param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_18;
  
  local_18 = param_4;
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = 0x21;
  }
  else if (param_2 == (int *)0x0) {
    iVar1 = 6;
  }
  else {
    uVar2 = *param_1;
    iVar1 = ft_mem_alloc(uVar2,0x78,&local_18);
    if (local_18 == 0) {
      *(undefined4 **)(iVar1 + 0x74) = param_1;
      FUN_0056865e(iVar1 + 0x34,uVar2);
      FUN_0056865e(iVar1 + 0x54,uVar2);
    }
    *param_2 = iVar1;
    iVar1 = local_18;
  }
  return CONCAT44(local_18,iVar1);
}

