
void FUN_00492288(int param_1)

{
  int iVar1;
  byte bVar2;
  
  if (*(ushort *)(param_1 + 0x12) < 100) {
    *(short *)(param_1 + 0x12) = *(short *)(param_1 + 0x12) + 1;
  }
  for (bVar2 = 0; bVar2 < *(byte *)(param_1 + 0x7158); bVar2 = bVar2 + 1) {
    iVar1 = param_1 + (uint)bVar2 * 0x18;
    if (((*(int *)(iVar1 + 0x6434) != 0) && (*(short *)(iVar1 + 0x643c) != 0)) &&
       (*(short *)(iVar1 + 0x643c) = *(short *)(iVar1 + 0x643c) + -1,
       *(short *)(iVar1 + 0x643c) == 0)) {
      if (*(int *)(iVar1 + 0x6438) != 0) {
        (**(code **)(iVar1 + 0x6438))(param_1,*(undefined4 *)(iVar1 + 0x6444));
      }
      FUN_0049183e(param_1,bVar2,iVar1 + 0x6430);
    }
  }
  return;
}

