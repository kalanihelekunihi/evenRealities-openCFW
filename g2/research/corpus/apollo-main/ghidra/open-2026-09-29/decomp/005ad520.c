
undefined4 cff_parse_maxstack(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = *(int *)(param_1 + 0x20);
  uVar3 = 0;
  if (iVar2 == 0) {
    uVar3 = 3;
  }
  else {
    uVar1 = cff_parse_num(param_1,*(undefined4 *)(param_1 + 0x10));
    *(undefined4 *)(iVar2 + 0xb8) = uVar1;
    if (0x201 < *(uint *)(iVar2 + 0xb8)) {
      *(undefined4 *)(iVar2 + 0xb8) = 0x201;
    }
    if (*(uint *)(iVar2 + 0xb8) < 0x201) {
      *(undefined4 *)(iVar2 + 0xb8) = 0x201;
    }
  }
  return uVar3;
}

