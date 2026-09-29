
void FT_Stream_ReleaseFrame(int param_1,undefined4 *param_2)

{
  if ((param_1 != 0) && (*(int *)(param_1 + 0x14) != 0)) {
    ft_mem_free(*(undefined4 *)(param_1 + 0x1c),*param_2);
    *param_2 = 0;
  }
  *param_2 = 0;
  return;
}

