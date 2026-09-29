
undefined4 cff_parse_private_dict(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = *(int *)(param_1 + 0x20);
  iVar4 = *(int *)(param_1 + 0x10);
  uVar1 = 0xa1;
  if (*(int *)(param_1 + 0x10) + 8U <= *(uint *)(param_1 + 0x14)) {
    iVar2 = cff_parse_num(param_1,iVar4);
    if (iVar2 < 0) {
      uVar1 = 3;
    }
    else {
      *(int *)(iVar3 + 0x78) = iVar2;
      iVar4 = cff_parse_num(param_1,iVar4 + 4);
      if (iVar4 < 0) {
        uVar1 = 3;
      }
      else {
        *(int *)(iVar3 + 0x74) = iVar4;
        uVar1 = 0;
      }
    }
  }
  return uVar1;
}

