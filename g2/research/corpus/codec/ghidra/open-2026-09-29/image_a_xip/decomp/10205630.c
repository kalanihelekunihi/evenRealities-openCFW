
void gx8002_npu_set_idle_mode(undefined4 param_1,int param_2)

{
  if (param_2 == 0) {
    gx8002_reg_set_bit(param_1,4);
  }
  else {
    gx8002_reg_clear_bit(param_1,4);
  }
  return;
}

