
undefined4 FUN_005e08d0(int param_1,undefined4 *param_2,byte *param_3,char param_4)

{
  undefined4 uVar1;
  ushort *puVar2;
  byte *pbVar3;
  byte *pbVar4;
  
  pbVar3 = (byte *)*param_2;
  puVar2 = *(ushort **)(param_1 + 0xc);
  if (param_3 < pbVar3 + 5) {
LAB_005e08dc:
    uVar1 = 6;
  }
  else {
    *puVar2 = (ushort)*pbVar3;
    puVar2[1] = (ushort)pbVar3[1];
    puVar2[2] = (short)(char)pbVar3[2];
    puVar2[3] = (short)(char)pbVar3[3];
    puVar2[4] = (ushort)pbVar3[4];
    pbVar4 = pbVar3 + 5;
    if (param_4 == '\0') {
      puVar2[5] = 0;
      puVar2[6] = 0;
      puVar2[7] = 0;
    }
    else {
      if (param_3 < pbVar3 + 8) goto LAB_005e08dc;
      puVar2[5] = (short)(char)*pbVar4;
      puVar2[6] = (short)(char)pbVar3[6];
      puVar2[7] = (ushort)pbVar3[7];
      pbVar4 = pbVar3 + 8;
    }
    *(undefined1 *)(param_1 + 0x10) = 1;
    *param_2 = pbVar4;
    uVar1 = 0;
  }
  return uVar1;
}

