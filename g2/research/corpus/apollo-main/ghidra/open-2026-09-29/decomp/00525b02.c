
void memory_stream_close(undefined4 *param_1)

{
  ft_mem_free(param_1[7],*param_1);
  *param_1 = 0;
  param_1[1] = 0;
  *param_1 = 0;
  param_1[6] = 0;
  return;
}

