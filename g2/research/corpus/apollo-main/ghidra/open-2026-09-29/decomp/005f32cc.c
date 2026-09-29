
undefined8 TT_Set_Named_Instance(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  iVar1 = 6;
  local_20 = param_3;
  uStack_1c = param_4;
  if (((*(int *)(param_1 + 700) == 0) && (iVar1 = TT_Get_MM_Var(param_1,0), iVar1 != 0)) ||
     (puVar3 = *(undefined4 **)(*(int *)(param_1 + 700) + 0xc),
     *(uint *)(param_1 + 0xc) >> 0x10 < param_2)) goto LAB_005f3368;
  if ((param_2 == 0) || (puVar3[4] == 0)) {
    iVar1 = TT_Set_Var_Design(param_1,0,0);
  }
  else {
    uVar4 = *(undefined4 *)(param_1 + 100);
    iVar2 = puVar3[4] + param_2 * 0xc;
    iVar1 = (**(code **)(*(int *)(param_1 + 0x21c) + 0x74))
                      (param_1,*(uint *)(iVar2 + -8) & 0xffff,&local_20);
    if (iVar1 != 0) goto LAB_005f3368;
    ft_mem_free(uVar4,*(undefined4 *)(param_1 + 0x18));
    *(undefined4 *)(param_1 + 0x18) = 0;
    *(undefined4 *)(param_1 + 0x18) = local_20;
    iVar1 = TT_Set_Var_Design(param_1,*puVar3,*(undefined4 *)(iVar2 + -0xc));
    if (iVar1 != 0) goto LAB_005f3368;
  }
  *(uint *)(param_1 + 4) = *(uint *)(param_1 + 4) & 0xffff | param_2 << 0x10;
  *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) & 0xffff7fff;
LAB_005f3368:
  return CONCAT44(local_20,iVar1);
}

