
void destroy_charmaps(int param_1,undefined4 param_2)

{
  int iVar1;
  
  if (param_1 != 0) {
    for (iVar1 = 0; iVar1 < *(int *)(param_1 + 0x24); iVar1 = iVar1 + 1) {
      ft_cmap_done_internal(*(undefined4 *)(*(int *)(param_1 + 0x28) + iVar1 * 4));
      *(undefined4 *)(*(int *)(param_1 + 0x28) + iVar1 * 4) = 0;
    }
    ft_mem_free(param_2,*(undefined4 *)(param_1 + 0x28));
    *(undefined4 *)(param_1 + 0x28) = 0;
    *(undefined4 *)(param_1 + 0x24) = 0;
  }
  return;
}

