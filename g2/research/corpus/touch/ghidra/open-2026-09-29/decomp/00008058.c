
undefined4 CheckLastWrittenRowIntegrity(undefined4 *param_1,ushort *param_2)

{
  ushort uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  if (*(char *)((int)param_2 + 0xd) == '\0') {
    iVar5 = *(int *)(param_2 + 0xc);
    uVar1 = param_2[1];
    iVar3 = CheckRowChecksum(iVar5,uVar1);
    if (iVar3 == 0) {
      uVar2 = GetStoredSeqNum(iVar5);
      uVar4 = 0;
    }
    else if ((char)param_2[7] == '\0') {
      DefineLastWrittenRow(param_2);
      uVar4 = *(undefined4 *)(param_2 + 0xc);
      iVar3 = CheckRowChecksum(uVar4,param_2[1]);
      if (iVar3 == 0) {
        uVar2 = GetStoredSeqNum(uVar4);
        uVar4 = DAT_00008108;
      }
      else {
        uVar2 = 0;
        uVar4 = DAT_00008108;
      }
    }
    else {
      iVar5 = iVar5 + (uint)*param_2 * (uint)(byte)param_2[6] * (uint)(uVar1 >> 2) * 4;
      iVar3 = CheckRowChecksum(iVar5,uVar1);
      if (iVar3 == 0) {
        uVar2 = GetStoredSeqNum(iVar5);
        uVar4 = DAT_00008104;
      }
      else {
        DefineLastWrittenRow(param_2);
        uVar4 = *(undefined4 *)(param_2 + 0xc);
        iVar3 = CheckRowChecksum(uVar4,param_2[1]);
        if (iVar3 == 0) {
          uVar2 = GetStoredSeqNum(uVar4);
          uVar4 = DAT_00008108;
        }
        else {
          uVar2 = 0;
          uVar4 = DAT_00008108;
        }
      }
    }
  }
  else {
    uVar2 = 0;
    uVar4 = 0;
  }
  *param_1 = uVar2;
  return uVar4;
}

