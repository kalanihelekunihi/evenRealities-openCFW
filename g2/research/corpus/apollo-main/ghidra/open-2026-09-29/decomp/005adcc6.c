
undefined4 cff_index_get_string(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  if (param_2 < *(uint *)(param_1 + 0x54c)) {
    uVar1 = *(undefined4 *)(*(int *)(param_1 + 0x550) + param_2 * 4);
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

