
longlong semantic_OtaFrameDispatch(char param_1,undefined1 *param_2,ushort param_3)

{
  uint unaff_r7;
  
  if (param_1 == -0x40) {
    _fileCmdParse(*param_2,param_2 + 1,param_3 - 1);
  }
  else if (param_1 == -0x3f) {
    _fileRawDataParse(param_2,param_3);
  }
  else if ((param_1 == -0x3e) || (param_1 == -0x3d)) {
    _exportFileParse(*param_2,param_2 + 1,param_3 - 1);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

