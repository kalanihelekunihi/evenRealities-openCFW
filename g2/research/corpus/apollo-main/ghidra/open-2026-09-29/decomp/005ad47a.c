
undefined8 cff_parse_vsindex(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 0x20);
  if ((iVar2 == 0) || (*(int *)(iVar2 + 0x16c) == 0)) {
    uVar1 = 3;
  }
  else if (*(char *)(*(int *)(iVar2 + 0x16c) + 0x22d) == '\0') {
    uVar1 = cff_parse_num(param_1,*(undefined4 *)(param_1 + 0x10));
    *(undefined4 *)(iVar2 + 0x168) = uVar1;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xa0;
  }
  return CONCAT44(param_4,uVar1);
}

