
void FUN_004992cc(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((*(uint *)(param_1 + 0x58) & 0xfff) >> 8 == 0xb) {
    FUN_004988dc(param_1,0);
    FUN_00498a14(param_1,0,0);
    if ((*(int *)(param_1 + 0x3c) != 0) && (*(int *)(param_1 + 0x40) != 0)) {
      FUN_0043f66c(param_1);
      iVar1 = FUN_0043fd9e(param_1);
      iVar3 = *(int *)(param_1 + 0x3c);
      iVar2 = FUN_0043fdda(param_1);
      FUN_004991e0(param_1,(iVar1 << 8) / iVar3,(iVar2 << 8) / *(int *)(param_1 + 0x40));
    }
  }
  else if ((*(uint *)(param_1 + 0x58) & 0xfff) >> 8 == 0xc) {
    FUN_004988dc(param_1,0);
    FUN_00498a14(param_1,0,0);
    FUN_004991e0(param_1,0x100,0x100);
  }
  return;
}

