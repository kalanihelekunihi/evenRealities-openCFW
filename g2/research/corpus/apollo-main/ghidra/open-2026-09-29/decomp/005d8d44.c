
void FUN_005d8d44(undefined4 param_1,int param_2,uint param_3,undefined4 *param_4,undefined4 param_5
                 )

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  byte *pbVar4;
  byte bVar5;
  undefined4 *local_18;
  
  local_18 = param_4;
  iVar1 = FUN_005d8d18(param_1,param_5,&local_18);
  if ((iVar1 == 0) && (iVar1 = FUN_005d8bc0(local_18,param_4,param_5), iVar1 == 0)) {
    *local_18 = param_4;
    pbVar4 = (byte *)(param_2 + (param_3 >> 3));
    uVar2 = (uint)(0x80 >> (param_3 & 7));
    pbVar3 = (byte *)local_18[2];
    iVar1 = 0x80;
    for (; param_4 != (undefined4 *)0x0; param_4 = (undefined4 *)((int)param_4 + -1)) {
      bVar5 = *pbVar3 & ~(byte)iVar1;
      if ((*pbVar4 & uVar2) != 0) {
        bVar5 = bVar5 | (byte)iVar1;
      }
      *pbVar3 = bVar5;
      uVar2 = (int)uVar2 >> 1;
      if (uVar2 == 0) {
        pbVar4 = pbVar4 + 1;
        uVar2 = 0x80;
      }
      iVar1 = iVar1 >> 1;
      if (iVar1 == 0) {
        pbVar3 = pbVar3 + 1;
        iVar1 = 0x80;
      }
    }
  }
  return;
}

