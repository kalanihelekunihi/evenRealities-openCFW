
int FUN_005942aa(uint param_1,int param_2)

{
  byte *pbVar1;
  
  pbVar1 = DAT_005947cc;
  *DAT_005947cc = (byte)(param_1 >> 4) & 1 ^ 1;
  if (*pbVar1 != 0) {
    param_2 = param_2 + 0x48;
  }
  return param_2;
}

