
int FUN_00544af2(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  
  bVar1 = false;
  while( true ) {
    iVar2 = FUN_00544814(param_1,param_2,param_3);
    if (iVar2 != -1) {
      return iVar2;
    }
    if ((*(char *)(param_1 + 0xc) == '\0') || (bVar1)) break;
    FUN_00544c78(param_1,param_3);
    bVar1 = true;
  }
  if (!bVar1) {
    return -1;
  }
  FUN_004733ee(DAT_00544b6c);
  uVar3 = FUN_00585c94(param_1);
  FUN_004733ee(DAT_00544b70,*param_1,uVar3);
  FUN_004733ee(DAT_00545530,param_3);
  *(undefined1 *)(param_1 + 0xc) = 0;
  return -1;
}

