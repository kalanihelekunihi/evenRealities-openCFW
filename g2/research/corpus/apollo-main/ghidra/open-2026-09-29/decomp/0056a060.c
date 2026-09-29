
byte * hciEvtParseVendorSpecCmdStatus(int param_1,byte *param_2)

{
  *(ushort *)(param_1 + 4) = (ushort)param_2[1] * 0x100 + (ushort)*param_2;
  return param_2 + 2;
}

