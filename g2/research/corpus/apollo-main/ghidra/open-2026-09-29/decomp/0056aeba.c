
void hciEvtParseReadLocalSupCtrDlyCmdCmpl(int param_1,undefined1 *param_2)

{
  *(undefined1 *)(param_1 + 4) = *param_2;
  *(uint *)(param_1 + 8) =
       (uint)(byte)param_2[2] * 0x100 + (uint)(byte)param_2[1] + (uint)(byte)param_2[3] * 0x10000;
  *(uint *)(param_1 + 0xc) =
       (uint)(byte)param_2[5] * 0x100 + (uint)(byte)param_2[4] + (uint)(byte)param_2[6] * 0x10000;
  *(undefined1 *)(param_1 + 3) = *(undefined1 *)(param_1 + 4);
  return;
}

