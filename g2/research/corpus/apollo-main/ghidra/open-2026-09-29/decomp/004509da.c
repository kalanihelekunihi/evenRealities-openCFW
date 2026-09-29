
void FUN_004509da(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_00450b30;
  *(undefined1 *)(DAT_00450b30 + 0xa4) = 1;
  iVar2 = FUN_00482cd8(iVar1 + 0xac);
  if (iVar2 == 0) {
    FUN_0046450c(*(undefined4 *)(iVar1 + 0xa8));
  }
  else {
    FUN_0046453e(*(undefined4 *)(iVar1 + 0xa8));
  }
  return;
}

