
void cff_charset_free_cids(int param_1,undefined4 param_2)

{
  ft_mem_free(param_2,*(undefined4 *)(param_1 + 0xc));
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(undefined4 *)(param_1 + 0x10) = 0;
  return;
}

