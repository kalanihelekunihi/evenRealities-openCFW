
void FUN_00440d70(int param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = FUN_0044ddea(param_1);
  for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
    FUN_00440d70(*(undefined4 *)(**(int **)(param_1 + 8) + uVar2 * 4));
  }
  if ((int)((uint)*(byte *)(param_1 + 0x2a) << 0x1f) < 0) {
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xfffe;
    FUN_0043f1a4(param_1);
    FUN_0043ffd0(param_1);
    if (uVar1 != 0) {
      FUN_004546f4(param_1);
    }
  }
  if ((*(ushort *)(param_1 + 0x2a) & 3) >> 1 != 0) {
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xfffd;
    FUN_0044f316(param_1,0);
  }
  return;
}

