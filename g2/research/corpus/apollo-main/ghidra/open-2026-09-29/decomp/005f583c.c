
void Ins_PUSHB(int param_1,int param_2)

{
  ushort uVar1;
  ushort uVar2;
  
  uVar2 = *(byte *)(param_1 + 0x174) - 0xaf;
  if ((uint)uVar2 < (uint)((*(int *)(param_1 + 0x14) + 1) - *(int *)(param_1 + 0x10))) {
    for (uVar1 = 1; uVar1 <= uVar2; uVar1 = uVar1 + 1) {
      *(uint *)(param_2 + (uint)uVar1 * 4 + -4) =
           (uint)*(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + (uint)uVar1);
    }
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x82;
  }
  return;
}

