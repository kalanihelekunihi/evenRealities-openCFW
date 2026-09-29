
undefined4 FUN_00533630(ushort *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  byte *pbVar3;
  ushort *puVar4;
  ushort uVar5;
  ushort uVar6;
  char cVar7;
  
  iVar2 = DAT_0053386c + (uint)*param_1 * 0x10;
  if (param_1[4] == 4) {
    pbVar3 = *(byte **)(param_1 + 2);
    uVar5 = (ushort)pbVar3[1] * 0x100 + (ushort)*pbVar3;
    uVar6 = (ushort)pbVar3[3] * 0x100 + (ushort)pbVar3[2];
    if ((uVar5 != 0) && (uVar5 <= uVar6)) {
      bVar1 = false;
      if (*(int *)(iVar2 + -0xc) != 0) {
        puVar4 = *(ushort **)(iVar2 + -0xc);
        for (cVar7 = *(char *)(iVar2 + -6); cVar7 != '\0'; cVar7 = cVar7 + -1) {
          if ((uVar5 <= *puVar4) && (*puVar4 <= uVar6)) {
            bVar1 = true;
            break;
          }
          puVar4 = puVar4 + 1;
        }
      }
      if ((bVar1) && (*(char *)(iVar2 + -5) != '\x01')) {
        FUN_00531f20((char)*param_1);
      }
    }
  }
  return param_4;
}

