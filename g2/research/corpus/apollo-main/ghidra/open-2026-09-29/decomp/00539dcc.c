
void attcProcPrepWriteRsp(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  if ((*(char *)(param_1 + 7) == '\x01') && (*(short *)(param_1 + 0x10) == 0)) {
    *(undefined1 *)(param_1 + 7) = 0;
  }
  *(int *)(param_4 + 4) = *(int *)(param_4 + 4) + 4;
  *(short *)(param_4 + 8) = *(short *)(param_4 + 8) + -4;
  return;
}

