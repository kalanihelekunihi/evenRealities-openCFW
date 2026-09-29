
undefined4
ft_glyphslot_set_bitmap(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ft_glyphslot_free_bitmap(param_1);
  *(undefined4 *)(param_1 + 0x58) = param_2;
  return param_4;
}

