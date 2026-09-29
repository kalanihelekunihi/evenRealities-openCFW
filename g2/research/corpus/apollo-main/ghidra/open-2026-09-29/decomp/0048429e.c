
void FUN_0048429e(undefined4 *param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  
  if ((param_2 != 0) && (iVar1 = FUN_00441c44(*param_1,0xffffffff), iVar1 == 1)) {
    uVar2 = FUN_004d05e4(param_2);
    FUN_004d0808(param_1[1],param_2);
    if (uVar2 < (uint)param_1[2]) {
      param_1[2] = param_1[2] - uVar2;
    }
    else {
      param_1[2] = 0;
    }
    FUN_004417ee(*param_1,0,0,0);
  }
  return;
}

