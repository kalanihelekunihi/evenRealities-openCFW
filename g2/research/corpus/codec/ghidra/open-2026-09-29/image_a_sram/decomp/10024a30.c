
void __reg_set_val(uint *param_1,uint param_2,int param_3,int param_4)

{
  *param_1 = param_3 << (param_2 & 0x3f) | *param_1 & ~(param_4 << (param_2 & 0x3f));
  return;
}

