
undefined4 DefineLastWrittenRow(ushort *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  int local_2c;
  
  iVar5 = *(int *)(param_1 + 8);
  *(int *)(param_1 + 0xc) = iVar5;
  if (*(char *)((int)param_1 + 0xd) == '\0') {
    uVar3 = (uint)*param_1 * (uint)(byte)param_1[6];
    uVar6 = 0;
    local_2c = iVar5;
    for (uVar7 = 0; uVar7 < uVar3; uVar7 = uVar7 + 1) {
      uVar1 = GetStoredSeqNum(iVar5);
      if ((uVar6 < uVar1) && (iVar2 = CheckRowChecksum(iVar5,param_1[1]), iVar2 == 0)) {
        uVar6 = uVar1;
        local_2c = iVar5;
      }
      iVar5 = iVar5 + (uint)(param_1[1] >> 2) * 4;
    }
    if ((char)param_1[7] == '\0') {
      uVar4 = 0;
    }
    else {
      uVar4 = 0;
      for (uVar7 = 0; uVar7 < uVar3; uVar7 = uVar7 + 1) {
        uVar1 = GetStoredSeqNum(iVar5);
        if ((uVar6 < uVar1) && (iVar2 = CheckRowChecksum(iVar5,param_1[1]), iVar2 == 0)) {
          uVar6 = uVar1;
          uVar4 = DAT_00008054;
          local_2c = iVar5;
        }
        iVar5 = iVar5 + (uint)(param_1[1] >> 2) * 4;
      }
    }
    *(int *)(param_1 + 0xc) = local_2c;
  }
  else {
    uVar4 = 0;
  }
  return uVar4;
}

