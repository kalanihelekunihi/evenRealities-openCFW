
void touch_state_16e6_blend_pair(int param_1,undefined2 *param_2,undefined2 *param_3)

{
  undefined2 uVar1;
  undefined2 uVar2;
  uint uVar3;
  
  uVar1 = *param_2;
  uVar2 = param_2[1];
  uVar3 = *(uint *)(param_1 + 0x70) >> 0x10 & 0xff;
  if ((int)(*(uint *)(param_1 + 0x70) << 0x1e) < 0) {
    uVar1 = touch_leaf_1cde_blend_u8(uVar1,*param_3,uVar3);
    *param_3 = uVar1;
    uVar2 = touch_leaf_1cde_blend_u8(uVar2,param_3[1],uVar3);
    param_3[1] = uVar2;
  }
  *param_2 = uVar1;
  param_2[1] = uVar2;
  return;
}

