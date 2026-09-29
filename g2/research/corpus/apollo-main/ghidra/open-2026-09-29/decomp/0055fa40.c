
void FUN_0055fa40(undefined4 *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  iVar1 = FUN_0055fc38(*param_1,0x40f,&local_18,1);
  if (iVar1 == DAT_0055fa98) {
    local_18 = CONCAT31(local_18._1_3_,
                        param_2 << (uint)(byte)PTR_DAT_0055faa4[*(byte *)(param_1 + 1)] &
                        PTR_DAT_0055faa0[*(byte *)(param_1 + 1)] |
                        (byte)local_18 & ~PTR_DAT_0055faa0[*(byte *)(param_1 + 1)]);
    FUN_0055fc2c(*param_1,0x40f,&local_18,1);
  }
  return;
}

