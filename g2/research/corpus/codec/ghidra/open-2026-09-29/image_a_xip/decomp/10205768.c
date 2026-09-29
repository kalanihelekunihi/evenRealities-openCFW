
void gx8002_npu_clr_interrupt(int param_1,uint param_2)

{
  if ((param_2 & 1) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0);
  }
  if ((param_2 & 2) != 0) {
    gx8002_reg_set_bit(param_1 + 8,4);
  }
  if ((param_2 & 4) != 0) {
    gx8002_reg_set_bit(param_1 + 8);
  }
  if ((param_2 & 8) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0xc);
  }
  if ((param_2 & 0x10) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0xd);
  }
  if ((param_2 & 0x20) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0xe);
  }
  if ((param_2 & 0x40) != 0) {
    gx8002_reg_set_bit(param_1 + 8,0x10);
  }
  return;
}

