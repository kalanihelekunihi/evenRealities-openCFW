
undefined4 LvpInitMode(int param_1)

{
  undefined4 *puVar1;
  undefined *puVar2;
  int iVar3;
  undefined4 uVar4;
  
  puVar1 = puRam102085ec;
  iVar3 = *piRam102085e8;
  uVar4 = 0;
  *puRam102085ec = 1;
  puVar1[1] = 0;
  if (param_1 != iVar3) {
    if (param_1 != *(int *)PTR_lvp_tws_mode_info_102085f0) goto LAB_102085c4;
    uVar4 = 1;
  }
  puVar1[1] = uVar4;
LAB_102085c4:
  puVar2 = PTR_PTR_102085f4;
  (*(code *)(*(uint *)(*(int *)(PTR_PTR_102085f4 + puVar1[1] * 4) + 0x10) & 0xfffffffe))();
  (*(code *)(*(uint *)(*(int *)(puVar2 + puVar1[1] * 4) + 4) & 0xfffffffe))(0xffff);
  return **(undefined4 **)(puVar2 + puVar1[1] * 4);
}

