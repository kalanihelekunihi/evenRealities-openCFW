
void case_interrupt_enable(uint param_1)

{
  if (-1 < (int)param_1) {
    *DAT_08005020 = 1 << (param_1 & 0x1f);
  }
  return;
}

