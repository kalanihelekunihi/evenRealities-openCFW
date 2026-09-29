
void ft_glyphslot_free_bitmap(int param_1)

{
  if ((*(int *)(param_1 + 0x9c) == 0) ||
     (-1 < (int)((uint)*(byte *)(*(int *)(param_1 + 0x9c) + 4) << 0x1f))) {
    *(undefined4 *)(param_1 + 0x58) = 0;
  }
  else {
    ft_mem_free(*(undefined4 *)(*(int *)(param_1 + 4) + 100),*(undefined4 *)(param_1 + 0x58));
    *(undefined4 *)(param_1 + 0x58) = 0;
    *(uint *)(*(int *)(param_1 + 0x9c) + 4) = *(uint *)(*(int *)(param_1 + 0x9c) + 4) & 0xfffffffe;
  }
  return;
}

