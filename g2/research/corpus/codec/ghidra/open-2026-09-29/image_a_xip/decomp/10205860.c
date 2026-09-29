
void gx8002_npu_get_over_cmd_addr(int param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  
  uVar1 = gx8002_reg_get_value(param_1 + 0x104);
  *param_2 = uVar1;
  return;
}

