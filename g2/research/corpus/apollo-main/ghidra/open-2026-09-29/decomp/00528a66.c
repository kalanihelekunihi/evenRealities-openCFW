
void FT_Stream_ExitFrame(undefined4 *param_1)

{
  if (param_1[5] != 0) {
    ft_mem_free(param_1[7],*param_1);
    *param_1 = 0;
  }
  param_1[8] = 0;
  param_1[9] = 0;
  return;
}

