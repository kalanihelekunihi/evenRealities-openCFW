
undefined1 semantic_slot_loaded(int param_1,int param_2)

{
  undefined1 uVar1;
  
  if ((*(char *)(param_1 * 0x414 + DAT_0058b530 + 0x40c) == '\x02') &&
     (*(int *)(DAT_0058b530 + param_1 * 0x414) == param_2)) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

