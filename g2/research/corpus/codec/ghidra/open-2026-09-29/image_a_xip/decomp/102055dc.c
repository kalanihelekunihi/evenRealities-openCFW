
void gx8002_reg_clear_bit(uint *param_1,uint param_2)

{
  *param_1 = (-2 << (param_2 & 0x3f) | 0xfffffffeU >> 0x20 - (param_2 & 0x3f)) & *param_1;
  return;
}

