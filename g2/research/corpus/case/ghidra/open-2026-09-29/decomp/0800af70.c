
void FUN_0800af70(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = DAT_0800afb0;
  uVar3 = 0;
  do {
    FUN_0800bf94(uVar3 * 0x14 + iVar1);
    uVar3 = uVar3 + 1;
  } while (uVar3 < 0x38);
  FUN_0800bf94(DAT_0800afb4);
  FUN_0800bf94(DAT_0800afb8);
  FUN_0800bf94(DAT_0800afbc);
  FUN_0800bf94(DAT_0800afc0);
  FUN_0800bf94(DAT_0800afc4);
  iVar2 = DAT_0800afc8;
  iVar1 = DAT_0800afb4;
  *(int *)(DAT_0800afc8 + 0x34) = DAT_0800afb4;
  *(int *)(iVar2 + 0x38) = iVar1 + 0x14;
  return;
}

