
void gx8002_npu_all_idle(int param_1)

{
  gx8002_reg_get_bit(param_1 + 0xc,0x1f);
  return;
}

