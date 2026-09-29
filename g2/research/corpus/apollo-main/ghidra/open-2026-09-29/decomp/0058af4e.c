
bool semantic_loading_timed_out(int param_1,int param_2,int param_3)

{
  bool bVar1;
  
  if (((*(char *)(param_1 * 0x414 + DAT_0058b530 + 0x40c) == '\x01') &&
      (*(int *)(DAT_0058b530 + param_1 * 0x414) == param_2)) &&
     (*(int *)(param_1 * 0x414 + DAT_0058b530 + 0x410) != 0)) {
    bVar1 = 4999 < (uint)(param_3 - *(int *)(param_1 * 0x414 + DAT_0058b530 + 0x410));
  }
  else {
    bVar1 = false;
  }
  return bVar1;
}

