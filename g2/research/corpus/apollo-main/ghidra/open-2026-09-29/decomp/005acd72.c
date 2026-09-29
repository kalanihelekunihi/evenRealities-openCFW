
void cff_parser_done(undefined4 *param_1)

{
  ft_mem_free(*(undefined4 *)*param_1,param_1[4]);
  param_1[4] = 0;
  return;
}

