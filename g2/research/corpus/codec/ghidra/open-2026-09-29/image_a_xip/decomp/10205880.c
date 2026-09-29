
void gx8002_npu_reset(int param_1)

{
  gx8002_reg_set_bit(param_1 + 4,3);
  gx8002_reg_set_bit(param_1 + 8,3);
  return;
}

