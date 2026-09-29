
uint gx8002_reg_get_bit(uint *param_1,uint param_2)

{
  return *param_1 >> (param_2 & 0x3f) & 1;
}

