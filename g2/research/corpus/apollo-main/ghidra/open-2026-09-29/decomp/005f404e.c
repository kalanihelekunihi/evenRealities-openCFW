
void ft_var_done_item_variation_store(int param_1,uint *param_2)

{
  undefined4 uVar1;
  uint uVar2;
  
  uVar1 = *(undefined4 *)(param_1 + 100);
  if (param_2[1] != 0) {
    for (uVar2 = 0; uVar2 < *param_2; uVar2 = uVar2 + 1) {
      ft_mem_free(uVar1,*(undefined4 *)(param_2[1] + uVar2 * 0x10 + 8));
      *(undefined4 *)(param_2[1] + uVar2 * 0x10 + 8) = 0;
      ft_mem_free(uVar1,*(undefined4 *)(param_2[1] + uVar2 * 0x10 + 0xc));
      *(undefined4 *)(param_2[1] + uVar2 * 0x10 + 0xc) = 0;
    }
    ft_mem_free(uVar1,param_2[1]);
    param_2[1] = 0;
  }
  if (param_2[4] != 0) {
    for (uVar2 = 0; uVar2 < param_2[3]; uVar2 = uVar2 + 1) {
      ft_mem_free(uVar1,*(undefined4 *)(param_2[4] + uVar2 * 4));
      *(undefined4 *)(param_2[4] + uVar2 * 4) = 0;
    }
    ft_mem_free(uVar1,param_2[4]);
    param_2[4] = 0;
  }
  return;
}

