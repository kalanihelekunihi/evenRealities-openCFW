
uint touch_leaf_1cde_blend_u8(int param_1,int param_2,int param_3)

{
  return (uint)(param_3 * param_1 + (0x100 - param_3) * param_2) >> 8;
}

