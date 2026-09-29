
int FUN_00597cde(undefined4 param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = 0;
  while( true ) {
    piVar1 = DAT_00597d24;
    if (*DAT_00597d20 <= uVar3) {
      return 0;
    }
    iVar2 = FUN_0046cacc(param_1,*DAT_00597d24 + uVar3 * 0x40 + 4);
    if (iVar2 == 0) break;
    uVar3 = uVar3 + 1;
  }
  return *piVar1 + uVar3 * 0x40;
}

