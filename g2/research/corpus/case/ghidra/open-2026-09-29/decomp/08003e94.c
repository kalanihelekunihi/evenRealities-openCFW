
void case_control_word5_set(uint param_1)

{
  *(uint *)(DAT_08003ea4 + 0x14) = *(uint *)(DAT_08003ea4 + 0x14) | param_1 | 0x10000;
  return;
}

