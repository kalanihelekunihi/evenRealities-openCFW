
undefined4 FUN_005686be(int *param_1,int *param_2,int *param_3)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  byte *pbVar5;
  
  iVar3 = 0;
  iVar4 = 0;
  pbVar5 = (byte *)param_1[3];
  bVar1 = false;
  for (iVar2 = *param_1; iVar2 != 0; iVar2 = iVar2 + -1) {
    if ((int)((uint)*pbVar5 << 0x1d) < 0) {
      if (bVar1) goto LAB_005686e2;
      bVar1 = true;
    }
    else if (!bVar1) goto LAB_005686e2;
    if ((int)((uint)*pbVar5 << 0x1c) < 0) {
      bVar1 = false;
      iVar4 = iVar4 + 1;
    }
    iVar3 = iVar3 + 1;
    pbVar5 = pbVar5 + 1;
  }
  if (bVar1) {
LAB_005686e2:
    iVar3 = 0;
    iVar4 = 0;
  }
  else {
    *(undefined1 *)(param_1 + 7) = 1;
  }
  *param_2 = iVar3;
  *param_3 = iVar4;
  return 0;
}

