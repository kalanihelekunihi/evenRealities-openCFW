
void Ins_SxyTCA(int param_1)

{
  byte bVar1;
  ushort uVar2;
  ushort uVar3;
  
  bVar1 = *(byte *)(param_1 + 0x174);
  uVar2 = (bVar1 & 1) << 0xe;
  uVar3 = uVar2 ^ 0x4000;
  if (bVar1 < 4) {
    *(ushort *)(param_1 + 0x12a) = uVar2;
    *(ushort *)(param_1 + 300) = uVar3;
    *(ushort *)(param_1 + 0x126) = uVar2;
    *(ushort *)(param_1 + 0x128) = uVar3;
  }
  if (-1 < (int)((uint)bVar1 << 0x1e)) {
    *(ushort *)(param_1 + 0x12e) = uVar2;
    *(ushort *)(param_1 + 0x130) = uVar3;
  }
  Compute_Funcs();
  return;
}

