
void touch_record_1e88_mask3(uint param_1,int param_2,uint *param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar3 = *param_3;
  *param_3 = uVar3 & ~param_1;
  uVar2 = param_3[1];
  param_3[1] = uVar2 & ~param_1;
  uVar1 = param_3[2];
  param_3[2] = uVar1 & ~param_1;
  if (param_2 << 0x1d < 0) {
    *param_3 = uVar3 | param_1;
  }
  if (param_2 << 0x1e < 0) {
    param_3[1] = uVar2 | param_1;
  }
  if (param_2 << 0x1f < 0) {
    param_3[2] = uVar1 | param_1;
  }
  return;
}

