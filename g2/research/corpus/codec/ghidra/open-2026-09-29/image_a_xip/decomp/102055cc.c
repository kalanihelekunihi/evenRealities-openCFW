
void gx8002_reg_set_bit(uint *param_1,uint param_2)

{
  *param_1 = 1 << (param_2 & 0x3f) | *param_1;
  return;
}

