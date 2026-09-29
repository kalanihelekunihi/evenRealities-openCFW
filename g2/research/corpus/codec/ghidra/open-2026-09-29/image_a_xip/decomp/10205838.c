
void gx8002_npu_clr_overflow_interrupt(int param_1,uint param_2)

{
  if ((param_2 & 0x10) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0xd);
  }
  if ((param_2 & 0x20) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0xe);
  }
  return;
}

