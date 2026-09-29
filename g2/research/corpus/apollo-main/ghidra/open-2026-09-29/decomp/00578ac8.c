
undefined4 semantic_CodecHostToBigEndian32(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = semantic_CodecHostIsLittleEndian();
  if (iVar1 != 0) {
    param_1 = semantic_CodecByteSwap32(param_1);
  }
  return param_1;
}

