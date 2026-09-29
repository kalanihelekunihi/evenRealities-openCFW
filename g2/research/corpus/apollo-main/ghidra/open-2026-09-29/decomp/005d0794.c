
undefined4 FUN_005d0794(undefined4 *param_1,byte *param_2)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  byte *pbVar4;
  byte *pbVar5;
  uint uVar6;
  
  iVar3 = 0;
  uVar2 = 3;
  pbVar4 = (byte *)*param_1;
  do {
    while( true ) {
      while( true ) {
        pbVar5 = pbVar4;
        if (param_2 <= pbVar4) goto LAB_005d080e;
        bVar1 = *pbVar4;
        pbVar5 = pbVar4 + 1;
        if (bVar1 != 0x5c) break;
        if (pbVar5 == param_2) goto LAB_005d080e;
        bVar1 = *pbVar5;
        if ((((bVar1 == 0x28) || (bVar1 == 0x29)) || (bVar1 == 0x5c)) ||
           (((bVar1 == 0x62 || (bVar1 == 0x66)) ||
            ((bVar1 == 0x6e || ((bVar1 == 0x72 || (bVar1 == 0x74)))))))) {
          pbVar4 = pbVar4 + 2;
        }
        else {
          uVar6 = 0;
          for (; ((pbVar4 = pbVar5, uVar6 < 3 && (pbVar5 < param_2)) && (*pbVar5 - 0x30 < 8));
              pbVar5 = pbVar5 + 1) {
            uVar6 = uVar6 + 1;
          }
        }
      }
      pbVar4 = pbVar5;
      if (bVar1 != 0x28) break;
      iVar3 = iVar3 + 1;
    }
  } while ((bVar1 != 0x29) || (iVar3 = iVar3 + -1, iVar3 != 0));
  uVar2 = 0;
LAB_005d080e:
  *param_1 = pbVar5;
  return uVar2;
}

