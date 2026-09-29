
longlong semantic_EfsFrameDispatch(char param_1,undefined1 *param_2,ushort param_3)

{
  uint unaff_r7;
  
  if (param_1 == -0x3c) {
    _efsFileCmdParse(*param_2,param_2 + 1,param_3 - 1);
  }
  else if (param_1 == -0x3b) {
    _efsFileRawDataParse(param_2,param_3);
  }
  else if ((param_1 == -0x3a) || (param_1 == -0x39)) {
    _efsExportFileParse(*param_2,param_2 + 1,param_3 - 1);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

