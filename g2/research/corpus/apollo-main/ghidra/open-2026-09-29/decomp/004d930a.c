
void FUN_004d930a(int *param_1)

{
  byte bVar1;
  uint uVar2;
  
  *(short *)(param_1 + 2) = (short)param_1[2] + 1;
  if (*(ushort *)(param_1 + 2) < *(ushort *)(*param_1 + 0x10)) {
    uVar2 = *(uint *)(*(int *)*param_1 + (uint)*(ushort *)((int)param_1 + 10) * 4);
    *(short *)((int)param_1 + 10) = (short)(1 << (uVar2 & 3)) + *(short *)((int)param_1 + 10);
    *(ushort *)(param_1 + 3) = (short)param_1[3] + (ushort)((uVar2 >> 8 & 0x30) == 0);
    if (((uVar2 >> 8 & 0xf) == 8) || ((uVar2 >> 8 & 0xf) == 9)) {
      bVar1 = 1;
    }
    else {
      bVar1 = 0;
    }
    *(ushort *)((int)param_1 + 0xe) = *(short *)((int)param_1 + 0xe) + (ushort)bVar1;
  }
  else {
    *(undefined2 *)(param_1 + 2) = 0;
    *(undefined2 *)((int)param_1 + 10) = 0;
    *(undefined2 *)((int)param_1 + 0xe) = 0;
    *(undefined2 *)(param_1 + 3) = 0;
  }
  return;
}

