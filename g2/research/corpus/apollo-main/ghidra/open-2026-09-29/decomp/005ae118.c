
void cff_vstore_done(uint *param_1,undefined4 param_2)

{
  uint uVar1;
  
  if (param_1[4] != 0) {
    for (uVar1 = 0; uVar1 < param_1[3]; uVar1 = uVar1 + 1) {
      ft_mem_free(param_2,*(undefined4 *)(param_1[4] + uVar1 * 4));
      *(undefined4 *)(param_1[4] + uVar1 * 4) = 0;
    }
  }
  ft_mem_free(param_2,param_1[4]);
  param_1[4] = 0;
  if (param_1[1] != 0) {
    for (uVar1 = 0; uVar1 < *param_1; uVar1 = uVar1 + 1) {
      ft_mem_free(param_2,*(undefined4 *)(param_1[1] + uVar1 * 8 + 4));
      *(undefined4 *)(param_1[1] + uVar1 * 8 + 4) = 0;
    }
  }
  ft_mem_free(param_2,param_1[1]);
  param_1[1] = 0;
  return;
}

