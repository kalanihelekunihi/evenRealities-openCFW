
undefined4 msc_sensing_loop(int param_1,int param_2,int param_3,uint *param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  uint local_40 [7];
  
  iVar2 = **(int **)(*param_5 + 8);
  *param_4 = 0;
  uVar5 = 0;
  for (uVar4 = 0; uVar4 < *(ushort *)(param_2 + 0x38); uVar4 = uVar4 + 1) {
    for (uVar3 = 0; uVar3 < 6; uVar3 = uVar3 + 1) {
      local_40[uVar3] = *(uint *)(uVar3 * 4 + param_1);
    }
    local_40[5] = local_40[5] & DAT_00006a6c | DAT_00006a70;
    local_40[3] = DAT_00006a74;
    local_40[4] = DAT_00006a78;
    msclp_scan_register_prepare(local_40,param_5);
    iVar1 = msclp_scan_start_wait(DAT_00006a7c,param_5);
    if (iVar1 == 0) {
      uVar5 = 4;
    }
    else {
      uVar3 = *(uint *)(iVar2 + 0x3200) & 0xffff;
      if (*param_4 < uVar3) {
        *param_4 = uVar3;
      }
    }
    param_1 = param_1 + param_3 * 4;
  }
  return uVar5;
}

