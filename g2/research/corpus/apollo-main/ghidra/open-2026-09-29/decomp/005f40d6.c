
int tt_done_blend(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  uVar2 = *(undefined4 *)(param_1 + 100);
  iVar1 = *(int *)(param_1 + 700);
  if (iVar1 != 0) {
    uVar3 = **(uint **)(iVar1 + 0xc);
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 4));
    *(undefined4 *)(iVar1 + 4) = 0;
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x14));
    *(undefined4 *)(iVar1 + 0x14) = 0;
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0xc));
    *(undefined4 *)(iVar1 + 0xc) = 0;
    if (*(int *)(iVar1 + 0x1c) != 0) {
      for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1) {
        ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x1c) + uVar4 * 8 + 4));
        *(undefined4 *)(*(int *)(iVar1 + 0x1c) + uVar4 * 8 + 4) = 0;
      }
      ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x1c));
      *(undefined4 *)(iVar1 + 0x1c) = 0;
    }
    if (*(int *)(iVar1 + 0x28) != 0) {
      ft_var_done_item_variation_store(param_1,*(undefined4 *)(iVar1 + 0x28));
      ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x28) + 0x1c));
      *(undefined4 *)(*(int *)(iVar1 + 0x28) + 0x1c) = 0;
      ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x28) + 0x18));
      *(undefined4 *)(*(int *)(iVar1 + 0x28) + 0x18) = 0;
      ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x28));
      *(undefined4 *)(iVar1 + 0x28) = 0;
    }
    if (*(int *)(iVar1 + 0x34) != 0) {
      ft_var_done_item_variation_store(param_1,*(undefined4 *)(iVar1 + 0x34));
      ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x34) + 0x1c));
      *(undefined4 *)(*(int *)(iVar1 + 0x34) + 0x1c) = 0;
      ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x34) + 0x18));
      *(undefined4 *)(*(int *)(iVar1 + 0x34) + 0x18) = 0;
      ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x34));
      *(undefined4 *)(iVar1 + 0x34) = 0;
    }
    if (*(int *)(iVar1 + 0x38) != 0) {
      ft_var_done_item_variation_store(param_1,*(int *)(iVar1 + 0x38) + 4);
      ft_mem_free(uVar2,*(undefined4 *)(*(int *)(iVar1 + 0x38) + 0x18));
      *(undefined4 *)(*(int *)(iVar1 + 0x38) + 0x18) = 0;
      ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x38));
      *(undefined4 *)(iVar1 + 0x38) = 0;
    }
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x40));
    *(undefined4 *)(iVar1 + 0x40) = 0;
    ft_mem_free(uVar2,*(undefined4 *)(iVar1 + 0x48));
    *(undefined4 *)(iVar1 + 0x48) = 0;
    ft_mem_free(uVar2,iVar1);
    param_1 = 0;
  }
  return param_1;
}

