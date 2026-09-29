
void FUN_0055ef80(undefined4 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_18;
  undefined4 local_14;
  
  local_18._1_3_ = (undefined3)((uint)param_3 >> 8);
  local_18 = CONCAT31(local_18._1_3_,*param_2) & 0xffffff07;
  local_18 = CONCAT31(local_18._1_3_,(byte)local_18 | (byte)(*(int *)(param_2 + 4) << 3) & 8);
  local_14 = param_4;
  iVar3 = FUN_0055fc2c(*param_1,0x705,&local_18,1);
  uVar2 = local_14;
  iVar1 = DAT_0055efec;
  if (iVar3 == DAT_0055efec) {
    local_14._3_1_ = SUB41(uVar2,3);
    local_14._0_3_ =
         CONCAT12((char)*(undefined4 *)(param_2 + 8),
                  CONCAT11((char)((uint)*(undefined4 *)(param_2 + 8) >> 8),
                           (char)((uint)*(undefined4 *)(param_2 + 8) >> 0x10)));
    iVar3 = FUN_0055fc2c(*param_1,0x708,&local_14,3);
    if (iVar3 == iVar1) {
      FUN_0055ef50(param_1,2);
    }
  }
  return;
}

