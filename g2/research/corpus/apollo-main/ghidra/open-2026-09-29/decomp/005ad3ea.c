
undefined8
cff_parse_multiple_master(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = *(int *)(param_1 + 0x20);
  uVar1 = 0xa1;
  if (*(int *)(param_1 + 0x10) + 0x14U <= *(uint *)(param_1 + 0x14)) {
    iVar2 = cff_parse_num(param_1,*(undefined4 *)(param_1 + 0x10));
    if (iVar2 - 2U < 0xf) {
      *(short *)(iVar3 + 0xb0) = (short)iVar2;
      *(short *)(iVar3 + 0xb2) =
           (short)(*(int *)(param_1 + 0x14) - *(int *)(param_1 + 0x10) >> 2) + -4;
      *(undefined2 *)(param_1 + 0x24) = *(undefined2 *)(iVar3 + 0xb0);
      *(undefined2 *)(param_1 + 0x26) = *(undefined2 *)(iVar3 + 0xb2);
      uVar1 = 0;
    }
    else {
      uVar1 = 3;
    }
  }
  return CONCAT44(param_4,uVar1);
}

