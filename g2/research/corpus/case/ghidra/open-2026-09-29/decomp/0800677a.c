
uint case_status_word2_bit0(int param_1)

{
  return *(uint *)(param_1 + 8) & 1;
}

