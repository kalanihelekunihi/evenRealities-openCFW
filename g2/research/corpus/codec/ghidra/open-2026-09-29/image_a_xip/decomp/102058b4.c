
void gx8002_npu_get_base_addr(int param_1,int param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  
  uVar1 = gx8002_reg_get_value(param_1 + param_2 * 4);
  *param_3 = uVar1;
  return;
}

