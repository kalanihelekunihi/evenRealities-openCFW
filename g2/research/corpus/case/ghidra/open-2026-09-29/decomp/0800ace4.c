
void FUN_0800ace4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_0800ad20;
  iVar1 = DAT_0800ad1c;
  iVar3 = *(int *)(DAT_0800ad1c + 4);
  while (iVar3 != 0) {
    FUN_0800bffc();
    iVar3 = *(int *)(*(int *)(iVar2 + 0xc) + 0xc);
    uxListRemove(iVar3 + 4);
    *(int *)(iVar1 + 8) = *(int *)(iVar1 + 8) + -1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + -1;
    FUN_0800c014();
    FUN_0800adb8(iVar3);
    iVar3 = *(int *)(iVar1 + 4);
  }
  return;
}

