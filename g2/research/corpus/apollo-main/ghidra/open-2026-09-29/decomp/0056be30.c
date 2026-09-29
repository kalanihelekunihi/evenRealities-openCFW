
undefined8 attcDiscProcChar(int param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  ushort uVar2;
  undefined4 uVar3;
  int iVar4;
  byte *pbVar5;
  undefined1 uVar6;
  
  if (*(char *)((int)param_2 + 3) == '\0') {
    iVar4 = *(int *)(param_2 + 2);
    uVar2 = param_2[4];
    bVar1 = **(byte **)(param_2 + 2);
    pbVar5 = *(byte **)(param_2 + 2) + 1;
    if (bVar1 == 7) {
      uVar6 = 0;
    }
    else {
      if (bVar1 != 0x15) {
        uVar3 = 0x73;
        goto LAB_0056beb2;
      }
      uVar6 = 1;
    }
    for (; pbVar5 < (byte *)(iVar4 + (uint)uVar2); pbVar5 = pbVar5 + bVar1) {
      attcDiscProcCharDecl(param_1,uVar6,pbVar5);
    }
  }
  if ((*(char *)((int)param_2 + 3) == '\0') && (*(char *)(param_2 + 6) != '\0')) {
    uVar3 = 0x79;
  }
  else {
    if (*(char *)(param_1 + 0x13) != -1) {
      *(undefined2 *)(*(int *)(param_1 + 4) + (uint)*(byte *)(param_1 + 0x13) * 2) =
           *(undefined2 *)(param_1 + 0x10);
    }
    *(undefined1 *)(param_1 + 0x12) = 0;
    uVar3 = attcDiscDescriptors((char)*param_2,param_1);
  }
LAB_0056beb2:
  return CONCAT44(param_4,uVar3);
}

