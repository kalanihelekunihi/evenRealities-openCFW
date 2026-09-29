
undefined4 cff_subfont_done(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  if (param_2 != 0) {
    cff_index_done(param_2 + 0x260);
    ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x284));
    *(undefined4 *)(param_2 + 0x284) = 0;
    ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x23c));
    *(undefined4 *)(param_2 + 0x23c) = 0;
    ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x244));
    *(undefined4 *)(param_2 + 0x244) = 0;
    ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x250));
    *(undefined4 *)(param_2 + 0x250) = 0;
  }
  return param_4;
}

