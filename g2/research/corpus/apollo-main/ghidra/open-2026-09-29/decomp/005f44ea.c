
void TT_Save_Context(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  *(undefined4 *)(param_2 + 0x7c) = *(undefined4 *)(param_1 + 400);
  *(undefined4 *)(param_2 + 0x88) = *(undefined4 *)(param_1 + 0x19c);
  *(undefined4 *)(param_2 + 0x94) = *(undefined4 *)(param_1 + 0x1a8);
  *(undefined4 *)(param_2 + 0x98) = *(undefined4 *)(param_1 + 0x1ac);
  for (iVar3 = 0; iVar3 < 3; iVar3 = iVar3 + 1) {
    iVar1 = param_1 + iVar3 * 8;
    uVar2 = *(undefined4 *)(iVar1 + 0x1c4);
    iVar4 = param_2 + iVar3 * 8;
    *(undefined4 *)(iVar4 + 0x9c) = *(undefined4 *)(iVar1 + 0x1c0);
    *(undefined4 *)(iVar4 + 0xa0) = uVar2;
  }
  return;
}

