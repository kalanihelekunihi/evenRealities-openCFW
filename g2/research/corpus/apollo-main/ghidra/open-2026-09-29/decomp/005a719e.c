
int af_cjk_snap_width(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  iVar2 = 0x62;
  iVar3 = param_3;
  for (uVar1 = 0; uVar1 < param_2; uVar1 = uVar1 + 1) {
    iVar4 = *(int *)(uVar1 * 0xc + param_1 + 4);
    iVar5 = param_3 - iVar4;
    if (iVar5 < 0) {
      iVar5 = -iVar5;
    }
    if (iVar5 < iVar2) {
      iVar2 = iVar5;
      iVar3 = iVar4;
    }
  }
  uVar1 = iVar3 + 0x20U & 0xffffffc0;
  if (param_3 < iVar3) {
    if ((int)(uVar1 - 0x30) < param_3) {
      param_3 = iVar3;
    }
  }
  else if (param_3 < (int)(uVar1 + 0x30)) {
    param_3 = iVar3;
  }
  return param_3;
}

