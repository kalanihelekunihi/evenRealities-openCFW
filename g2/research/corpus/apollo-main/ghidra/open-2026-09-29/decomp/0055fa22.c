
void FUN_0055fa22(undefined4 *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  uint local_10;
  undefined4 uStack_c;
  
  local_10._1_3_ = (undefined3)((uint)param_3 >> 8);
  local_10 = CONCAT31(local_10._1_3_,param_2) & 0xffffff1f;
  uStack_c = param_4;
  FUN_0055fc2c(*param_1,*(undefined2 *)(PTR_DAT_0055fa9c + (uint)*(byte *)(param_1 + 1) * 2),
               &local_10,1);
  return;
}

