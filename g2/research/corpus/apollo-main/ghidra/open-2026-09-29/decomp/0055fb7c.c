
undefined8 FUN_0055fb7c(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  int iVar3;
  undefined4 local_18;
  
  puVar2 = PTR_DAT_0055fc1c;
  local_18 = param_4;
  iVar3 = FUN_0055fc38(*param_1,*(undefined2 *)(PTR_DAT_0055fc1c + (uint)*(byte *)(param_1 + 1) * 2)
                       ,&local_18,1);
  iVar1 = DAT_0055fc08;
  if (iVar3 == DAT_0055fc08) {
    local_18 = CONCAT31(local_18._1_3_,
                        (param_2 != 0) << PTR_DAT_0055fc24[*(byte *)(param_1 + 1)] &
                        PTR_DAT_0055fc20[*(byte *)(param_1 + 1)] |
                        (byte)local_18 & ~PTR_DAT_0055fc20[*(byte *)(param_1 + 1)]);
    iVar3 = FUN_0055fc2c(*param_1,*(undefined2 *)(puVar2 + (uint)*(byte *)(param_1 + 1) * 2),
                         &local_18,1);
    if (iVar3 == iVar1) {
      iVar3 = iVar1;
    }
  }
  return CONCAT44(local_18,iVar3);
}

