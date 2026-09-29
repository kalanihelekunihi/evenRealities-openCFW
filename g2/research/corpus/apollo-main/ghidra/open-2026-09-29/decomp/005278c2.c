
undefined8 FT_Outline_New_Internal(int param_1,uint param_2,uint param_3,undefined2 *param_4)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined2 *local_18;
  
  uVar3 = param_2;
  if ((param_4 == (undefined2 *)0x0) || (param_1 == 0)) {
    local_18 = (undefined2 *)0x6;
    goto LAB_00527978;
  }
  local_18 = param_4;
  FUN_0048949c(param_4,0x14);
  if (((int)param_3 < 0) || (param_2 < param_3)) {
    local_18 = (undefined2 *)0x6;
    goto LAB_00527978;
  }
  if (0x7fff < param_2) {
    local_18 = (undefined2 *)0xa;
    goto LAB_00527978;
  }
  uVar3 = 0;
  uVar2 = ft_mem_realloc(param_1,8,0,param_2,0,&local_18);
  *(undefined4 *)(param_4 + 2) = uVar2;
  if (local_18 == (undefined2 *)0x0) {
    uVar3 = 0;
    uVar2 = ft_mem_realloc(param_1,1,0,param_2,0,&local_18);
    *(undefined4 *)(param_4 + 4) = uVar2;
    if (local_18 != (undefined2 *)0x0) goto LAB_0052794a;
    uVar3 = 0;
    uVar2 = ft_mem_realloc(param_1,2,0,param_3,0,&local_18);
    *(undefined4 *)(param_4 + 6) = uVar2;
    if (local_18 != (undefined2 *)0x0) goto LAB_0052794a;
    bVar1 = false;
  }
  else {
LAB_0052794a:
    bVar1 = true;
  }
  if (bVar1) {
    *(uint *)(param_4 + 8) = *(uint *)(param_4 + 8) | 1;
    FT_Outline_Done_Internal(param_1,param_4);
  }
  else {
    param_4[1] = (short)param_2;
    *param_4 = (short)param_3;
    *(uint *)(param_4 + 8) = *(uint *)(param_4 + 8) | 1;
    local_18 = (undefined2 *)0x0;
  }
LAB_00527978:
  return CONCAT44(uVar3,local_18);
}

