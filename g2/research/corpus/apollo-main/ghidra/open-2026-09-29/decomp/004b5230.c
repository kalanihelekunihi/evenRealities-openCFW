
void attcProcErrRsp(int param_1,undefined4 param_2,int param_3,int param_4)

{
  *(undefined1 *)(param_4 + 2) = *(undefined1 *)(param_1 + 6);
  if ((((*(char *)(param_4 + 2) != '\x05') && (*(char *)(param_4 + 2) != '\x06')) &&
      (*(char *)(param_4 + 2) != '\t')) && (*(char *)(param_4 + 2) != '\v')) {
    *(ushort *)(param_4 + 10) =
         (ushort)*(byte *)(param_3 + 0xb) * 0x100 + (ushort)*(byte *)(param_3 + 10);
  }
  *(undefined1 *)(param_4 + 3) = *(undefined1 *)(param_3 + 0xc);
  if (*(char *)(param_4 + 3) == '\0') {
    *(undefined1 *)(param_4 + 3) = 0x75;
  }
  *(undefined2 *)(param_4 + 8) = 0;
  return;
}

