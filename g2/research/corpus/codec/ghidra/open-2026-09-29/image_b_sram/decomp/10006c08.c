
undefined4 FUN_10006c08(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = DAT_10006c2c;
  iVar3 = *DAT_10006c28;
  if (*DAT_10006c28 == 0) {
    *DAT_10006c28 = DAT_10006c2c;
    iVar3 = iVar1;
  }
  if (*(uint *)(iVar3 + 4) != 0) {
    uVar2 = (*(code *)(*(uint *)(iVar3 + 4) & 0xfffffffe))();
    return uVar2;
  }
  return 0;
}

