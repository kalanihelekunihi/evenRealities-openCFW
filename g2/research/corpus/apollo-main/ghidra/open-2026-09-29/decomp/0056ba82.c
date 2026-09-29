
undefined8 attcDiscProcDesc(int *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  ushort uVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  char *pcVar6;
  byte bVar7;
  undefined1 uVar8;
  
  if (*(char *)((int)param_2 + 3) == '\0') {
    iVar5 = *(int *)(param_2 + 2);
    uVar2 = param_2[4];
    cVar1 = **(char **)(param_2 + 2);
    pcVar6 = *(char **)(param_2 + 2) + 1;
    if (cVar1 == '\x01') {
      uVar8 = 0;
      bVar7 = 4;
    }
    else {
      if (cVar1 != '\x02') {
        uVar4 = 0x73;
        goto LAB_0056bb16;
      }
      uVar8 = 1;
      bVar7 = 0x12;
    }
    for (; pcVar6 < (char *)(iVar5 + (uint)uVar2); pcVar6 = pcVar6 + bVar7) {
      attcDiscProcDescPair(param_1,uVar8,pcVar6);
    }
  }
  if ((*(char *)((int)param_2 + 3) == '\0') && (*(char *)(param_2 + 6) != '\0')) {
    uVar4 = 0x79;
  }
  else {
    piVar3 = (int *)(*param_1 + (uint)*(byte *)((int)param_1 + 0x12) * 4);
    do {
      *(char *)((int)param_1 + 0x12) = *(char *)((int)param_1 + 0x12) + '\x01';
      if (*(char *)((int)param_1 + 0x12) == (char)param_1[3]) break;
      piVar3 = piVar3 + 1;
    } while ((int)((uint)*(byte *)(*piVar3 + 4) << 0x1d) < 0);
    uVar4 = attcDiscDescriptors((char)*param_2,param_1);
  }
LAB_0056bb16:
  return CONCAT44(param_4,uVar4);
}

