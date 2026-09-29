
undefined4 af_shaper_buf_destroy(int param_1)

{
  undefined4 unaff_r7;
  
  ft_mem_free(*(undefined4 *)(param_1 + 100));
  return unaff_r7;
}

