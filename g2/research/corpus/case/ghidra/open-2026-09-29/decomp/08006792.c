
undefined4 case_status_word3_field10_clear(int param_1)

{
  if ((*(uint *)(param_1 + 0xc) & 0xfff) >> 10 != 0) {
    return 0;
  }
  return 1;
}

