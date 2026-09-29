
undefined2 cff_cmap_encoding_char_index(int param_1,uint param_2)

{
  undefined2 uVar1;
  
  uVar1 = 0;
  if (param_2 < 0x100) {
    uVar1 = *(undefined2 *)(*(int *)(param_1 + 0x10) + param_2 * 2);
  }
  return uVar1;
}

