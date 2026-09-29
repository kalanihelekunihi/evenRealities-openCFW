
undefined4 CheckRowChecksum(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = GetStoredRowChecksum();
  iVar2 = CalculateRowChecksum(param_1,param_2);
  uVar3 = DAT_00007f9c;
  if (iVar1 == iVar2) {
    uVar3 = 0;
  }
  return uVar3;
}

