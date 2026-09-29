
undefined4 FUN_0055553c(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = DAT_005560cc;
  for (uVar3 = 0; uVar3 < 4; uVar3 = uVar3 + 1) {
    iVar2 = FUN_0044dce2(*(undefined4 *)(param_1 + 0x18),uVar3);
    uVar4 = uVar3 + param_2;
    if (iVar2 != 0) {
      if (uVar4 < *(uint *)(iVar1 + 0xc)) {
        FUN_00555514(iVar2,uVar4);
        FUN_00554b2c(iVar2,uVar4);
      }
      else {
        FUN_0049942e(iVar2,&DAT_00555748);
      }
    }
  }
  return param_4;
}

