
undefined8
FT_Stream_ReadULong(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte *pbVar2;
  uint uVar3;
  undefined4 uStack_18;
  
  pbVar2 = (byte *)&uStack_18;
  uStack_18 = param_4;
  uVar3 = 0;
  *param_2 = 0;
  if (param_1[2] + 3U < (uint)param_1[1]) {
    if (param_1[5] == 0) {
      pbVar2 = (byte *)(*param_1 + param_1[2]);
    }
    else {
      iVar1 = (*(code *)param_1[5])(param_1,param_1[2],pbVar2,4);
      if (iVar1 != 4) goto LAB_00528c0c;
    }
    if (pbVar2 != (byte *)0x0) {
      uVar3 = (uint)pbVar2[3] |
              (uint)pbVar2[1] << 0x10 | (uint)*pbVar2 << 0x18 | (uint)pbVar2[2] << 8;
    }
    param_1[2] = param_1[2] + 4;
  }
  else {
LAB_00528c0c:
    *param_2 = 0x55;
    uVar3 = 0;
  }
  return CONCAT44(uStack_18,uVar3);
}

