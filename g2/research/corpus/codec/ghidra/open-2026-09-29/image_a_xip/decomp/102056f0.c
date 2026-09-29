
void gx8002_npu_get_interrupt(int param_1,uint *param_2)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = gx8002_reg_get_value(param_1 + 0xc);
  uVar2 = uVar1 & 1;
  if ((uVar1 & 0x10) != 0) {
    uVar2 = uVar2 | 2;
  }
  *param_2 = uVar2;
  if ((uVar1 & 0x100) != 0) {
    *param_2 = *param_2 | 4;
  }
  if ((uVar1 & 0x1000) != 0) {
    *param_2 = *param_2 | 8;
  }
  if ((uVar1 & 0x2000) != 0) {
    *param_2 = *param_2 | 0x10;
  }
  if ((uVar1 & 0x4000) != 0) {
    *param_2 = *param_2 | 0x20;
  }
  if ((uVar1 & 0x10000) != 0) {
    *param_2 = *param_2 | 0x40;
  }
  return;
}

