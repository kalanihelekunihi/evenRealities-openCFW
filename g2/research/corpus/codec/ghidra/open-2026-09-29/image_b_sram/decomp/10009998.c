
int gx8002_strncmp(byte *param_1,byte *param_2,int param_3)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  
  pbVar2 = param_2 + param_3;
  while( true ) {
    if (param_2 == pbVar2) {
      return 0;
    }
    bVar1 = *param_1;
    iVar3 = (uint)bVar1 - (uint)*param_2;
    if (iVar3 != 0) break;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
    if (bVar1 == 0) {
      return 0;
    }
  }
  return iVar3;
}

