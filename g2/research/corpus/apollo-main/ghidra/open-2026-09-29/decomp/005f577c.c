
void Ins_NPUSHB(int param_1,int param_2)

{
  byte bVar1;
  ushort uVar2;
  
  bVar1 = *(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + 1);
  if ((uint)bVar1 < (uint)((*(int *)(param_1 + 0x14) + 1) - *(int *)(param_1 + 0x10))) {
    for (uVar2 = 1; uVar2 <= bVar1; uVar2 = uVar2 + 1) {
      *(uint *)(param_2 + (uint)uVar2 * 4 + -4) =
           (uint)*(byte *)(*(int *)(param_1 + 0x168) + *(int *)(param_1 + 0x16c) + (uint)uVar2 + 1);
    }
    *(uint *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + (uint)bVar1;
  }
  else {
    *(undefined4 *)(param_1 + 0xc) = 0x82;
  }
  return;
}

