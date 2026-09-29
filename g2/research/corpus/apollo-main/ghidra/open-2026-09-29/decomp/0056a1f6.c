
void hciEvtParseReadMaxDataLenCmdCmpl(int param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  *(ushort *)(param_1 + 6) = (ushort)(byte)param_2[2] * 0x100 + (ushort)(byte)param_2[1];
  *(ushort *)(param_1 + 8) = (ushort)(byte)param_2[4] * 0x100 + (ushort)(byte)param_2[3];
  *(ushort *)(param_1 + 10) = (ushort)(byte)param_2[6] * 0x100 + (ushort)(byte)param_2[5];
  *(ushort *)(param_1 + 0xc) = (ushort)(byte)param_2[8] * 0x100 + (ushort)(byte)param_2[7];
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return;
}

