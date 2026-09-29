
void gx8002_npu_set_idle_cycle(undefined4 param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = gx8002_reg_get_value();
  gx8002_reg_set_value(param_1,uVar1 & 0xffff | param_2 << 0x10);
  return;
}

