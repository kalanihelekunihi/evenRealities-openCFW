
void Ins_WS(int param_1,uint *param_2)

{
  if (*param_2 < (uint)*(ushort *)(param_1 + 0x1d8)) {
    *(uint *)(*(int *)(param_1 + 0x1dc) + *param_2 * 4) = param_2[1];
  }
  else if (*(char *)(param_1 + 0x235) != '\0') {
    *(undefined4 *)(param_1 + 0xc) = 0x86;
  }
  return;
}

