
undefined4 cff_parse_cid_ros(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = *(int *)(param_1 + 0x20);
  iVar3 = *(int *)(param_1 + 0x10);
  uVar1 = 0xa1;
  if (*(int *)(param_1 + 0x10) + 0xcU <= *(uint *)(param_1 + 0x14)) {
    uVar1 = cff_parse_num(param_1,iVar3);
    *(undefined4 *)(iVar2 + 0x84) = uVar1;
    uVar1 = cff_parse_num(param_1,iVar3 + 4);
    *(undefined4 *)(iVar2 + 0x88) = uVar1;
    uVar1 = cff_parse_num(param_1);
    *(undefined4 *)(iVar2 + 0x8c) = uVar1;
    uVar1 = 0;
  }
  return uVar1;
}

