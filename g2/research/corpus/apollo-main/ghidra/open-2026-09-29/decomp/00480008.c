
void FUN_00480008(byte *param_1)

{
  int iVar1;
  
  iVar1 = *DAT_004801f4;
  *param_1 = (byte)((uint)iVar1 >> 8) & 3;
  param_1[1] = (byte)((uint)(iVar1 << 0x1a) >> 0x1e);
  param_1[2] = (byte)iVar1 & 3;
  return;
}

