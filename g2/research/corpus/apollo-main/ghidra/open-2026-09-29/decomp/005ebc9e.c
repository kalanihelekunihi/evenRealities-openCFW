
void FUN_005ebc9e(int param_1,char param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (((param_1 != 0) && (*(int *)(param_1 + 0x208) != 0)) && (*(int *)(param_1 + 0x200) != 0)) {
    iVar1 = *(int *)(*DAT_005ec2e0 + 0xc);
    iVar4 = 8;
    if (0x10 < iVar1) {
      iVar4 = (iVar1 + -0x10) / 2 + 8;
    }
    iVar2 = FUN_0043fc70(*(undefined4 *)(param_1 + 0x200));
    iVar3 = FUN_0043fce0(*(undefined4 *)(param_1 + 0x200));
    iVar4 = iVar4 + iVar3;
    if (param_2 == '\x01') {
      iVar4 = iVar1 + iVar4 + 2;
    }
    FUN_0043f09a(*(undefined4 *)(param_1 + 0x208),iVar2 + -0x14,iVar4);
  }
  return;
}

