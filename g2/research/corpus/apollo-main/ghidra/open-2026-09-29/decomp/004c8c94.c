
undefined4 FUN_004c8c94(byte param_1,int param_2,uint param_3,int param_4,int param_5,int param_6)

{
  int iVar1;
  uint uVar2;
  byte *pbVar3;
  int iVar4;
  
  if (param_1 == 7) {
    iVar1 = 1;
    pbVar3 = (byte *)(param_5 + (int)param_3 / 8);
    uVar2 = 7 - (param_3 & 7);
  }
  else {
    if (param_1 < 7) {
      return 0;
    }
    if (param_1 == 9) {
      iVar1 = 4;
      pbVar3 = (byte *)(param_5 + (int)param_3 / 2);
      uVar2 = (param_3 & 1) * -4 + 4;
    }
    else if (param_1 < 9) {
      iVar1 = 2;
      pbVar3 = (byte *)(param_5 + (int)param_3 / 4);
      uVar2 = (param_3 & 3) * -2 + 6;
    }
    else {
      if (param_1 != 10) {
        return 0;
      }
      iVar1 = 8;
      pbVar3 = (byte *)(param_5 + param_3);
      uVar2 = 0;
    }
  }
  for (iVar4 = 0; iVar4 < param_4; iVar4 = iVar4 + 1) {
    *(undefined4 *)(param_6 + iVar4 * 4) =
         *(undefined4 *)
          (param_2 + ((1 << iVar1) - 1U & (int)(uint)*pbVar3 >> (uVar2 & 0xff) & 0xff) * 4);
    uVar2 = uVar2 - iVar1;
    if ((char)uVar2 < '\0') {
      uVar2 = 8 - iVar1;
      pbVar3 = pbVar3 + 1;
    }
  }
  return 1;
}

