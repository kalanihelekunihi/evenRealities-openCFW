
void FUN_004ed824(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  piVar1 = DAT_004eda7c;
  if ((*DAT_004eda7c != 0) && (iVar3 = *DAT_004eda80, 0 < iVar3 + -0x100)) {
    iVar2 = FUN_0043fdda(*DAT_004eda7c);
    iVar3 = -(((0x100 - iVar2) * param_1) / (iVar3 + -0x100));
    if (iVar3 < 0) {
      iVar3 = 0;
    }
    if (0x100 - iVar2 < iVar3) {
      iVar3 = 0x100 - iVar2;
    }
    FUN_0043f142(*piVar1,iVar3);
  }
  return;
}

