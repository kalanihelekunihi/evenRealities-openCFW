
undefined2 cff_charset_cid_to_gindex(int param_1,uint param_2)

{
  undefined2 uVar1;
  
  uVar1 = 0;
  if (param_2 <= *(uint *)(param_1 + 0x10)) {
    uVar1 = *(undefined2 *)(*(int *)(param_1 + 0xc) + param_2 * 2);
  }
  return uVar1;
}

