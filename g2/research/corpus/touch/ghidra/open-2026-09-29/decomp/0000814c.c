
undefined4 CopyHistoricData(int param_1,undefined4 param_2,ushort *param_3)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar1 = param_3[1];
  iVar2 = GetReadRowPointer(param_2,param_3);
  iVar3 = CheckRowChecksum(iVar2,uVar1);
  if (iVar3 == 0) {
    iVar3 = (uint)(uVar1 >> 3) * 4;
    iVar2 = (*(code *)(*(undefined4 **)(param_3 + 0xe))[5])
                      (**(undefined4 **)(param_3 + 0xe),iVar2 + iVar3,param_3[10],param_1 + iVar3);
    uVar4 = 0;
    if (iVar2 != 0) {
      uVar4 = DAT_000081fc;
    }
  }
  else {
    uVar4 = DAT_000081f4;
    if ((char)param_3[7] != '\0') {
      iVar2 = iVar2 + (uint)*param_3 * (uint)(byte)param_3[6] * (uint)(uVar1 >> 2) * 4;
      iVar3 = CheckRowChecksum(iVar2,uVar1);
      uVar4 = DAT_000081f4;
      if ((iVar3 == 0) &&
         (iVar3 = (uint)(uVar1 >> 3) * 4,
         iVar3 = (*(code *)(*(undefined4 **)(param_3 + 0xe))[5])
                           (**(undefined4 **)(param_3 + 0xe),iVar2 + iVar3,param_3[10],
                            param_1 + iVar3), uVar4 = DAT_000081fc, iVar3 == 0)) {
        uVar4 = DAT_000081f8;
      }
    }
    iVar3 = GetStoredSeqNum(iVar2);
    if ((iVar3 == 0) && (iVar2 = GetStoredRowChecksum(iVar2), iVar2 == 0)) {
      uVar4 = 0;
    }
  }
  return uVar4;
}

