
int FUN_00522602(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_00522e98;
  if (*DAT_00522e98 == 0) {
    iVar2 = FUN_0051403c(0x1f0);
    *piVar1 = iVar2;
  }
  return *piVar1;
}

