
void attcProcReadLongRsp(int *param_1,ushort param_2,undefined4 param_3,int param_4)

{
  if (*(char *)((int)param_1 + 7) == '\x01') {
    if (param_2 < *(ushort *)(*param_1 + (uint)*(byte *)(param_1 + 10) * 4)) {
      *(undefined1 *)((int)param_1 + 7) = 0;
    }
    else {
      *(short *)((int)param_1 + 0x12) = *(short *)(param_4 + 8) + *(short *)((int)param_1 + 0x12);
    }
  }
  return;
}

