
undefined8
cff_index_read_offset(undefined4 *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 local_18 [2];
  
  uVar3 = 0;
  local_18[0] = param_3;
  local_18[1] = param_4;
  iVar1 = FT_Stream_Read(*param_1,local_18,*(undefined1 *)(param_1 + 4));
  if (iVar1 == 0) {
    for (iVar2 = 0; iVar2 < (int)(uint)*(byte *)(param_1 + 4); iVar2 = iVar2 + 1) {
      uVar3 = (uint)*(byte *)((int)local_18 + iVar2) | uVar3 << 8;
    }
  }
  *param_2 = iVar1;
  return CONCAT44(local_18[0],uVar3);
}

