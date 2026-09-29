
void touch_pipeline_1d54_blend(int param_1,ushort *param_2,ushort *param_3,undefined1 *param_4)

{
  ushort uVar1;
  undefined4 uVar2;
  
  uVar1 = *(ushort *)(param_1 + 0x74) & 0x300;
  if (uVar1 == 0x200) {
    uVar2 = touch_leaf_1cde_blend_u8
                      ((uint)*param_2 << 8,(uint)CONCAT21(*param_3,*param_4),
                       *(undefined4 *)(param_1 + 0x24),(uint)*param_3 << 8,param_4);
    uVar1 = (ushort)((uint)uVar2 >> 8);
    *param_3 = uVar1;
    *param_4 = (char)uVar2;
    *param_2 = uVar1;
  }
  else {
    uVar1 = touch_leaf_1cde_blend_u8
                      (*param_2,*param_3,*(undefined4 *)(param_1 + 0x24),uVar1,param_4);
    *param_3 = uVar1;
    *param_2 = uVar1;
  }
  return;
}

