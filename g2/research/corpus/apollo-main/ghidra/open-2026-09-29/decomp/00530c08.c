
void hciCoreNumCmplPkts(char *param_1)

{
  byte bVar1;
  int iVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  byte *pbVar6;
  char cVar7;
  
  cVar7 = '\0';
  pbVar6 = (byte *)(param_1 + 1);
  cVar3 = *param_1;
  while (cVar4 = cVar3 + -1, cVar3 != '\0') {
    iVar5 = (uint)pbVar6[1] * 0x100 + (uint)*pbVar6;
    bVar1 = pbVar6[2];
    pbVar6 = pbVar6 + 4;
    iVar2 = hciCoreConnByHandle(iVar5);
    cVar3 = cVar4;
    if (iVar2 != 0) {
      *(byte *)(iVar2 + 0x19) = *(char *)(iVar2 + 0x19) - bVar1;
      *(byte *)(iVar2 + 0x18) = *(char *)(iVar2 + 0x18) - bVar1;
      cVar7 = bVar1 + cVar7;
      if ((*(char *)(iVar2 + 0x17) != '\0') &&
         (*(byte *)(iVar2 + 0x18) <= *(byte *)(DAT_00530d68 + 0x81))) {
        *(undefined1 *)(iVar2 + 0x17) = 0;
        (**(code **)(DAT_00530d6c + 0x14))(iVar5,0);
      }
    }
  }
  hciCoreTxReady(cVar7);
  return;
}

