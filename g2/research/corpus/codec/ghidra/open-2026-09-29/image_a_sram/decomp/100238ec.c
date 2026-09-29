
int gx8002_flash_write_protect_status(int *param_1)

{
  short sVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  byte *pbVar5;
  int *piVar6;
  int iVar7;
  
  iVar4 = DAT_1002397c;
  *param_1 = 0;
  piVar6 = *(int **)(*(int *)(iVar4 + 0xc) + 0x10);
  if ((piVar6 != (int *)0x0) && (*piVar6 != 0)) {
    gx8002_flash_wait_ready();
    sVar1 = *(short *)(*(int *)(iVar4 + 0xc) + 6);
    if ((sVar1 == 0x5e) || (sVar1 == 0x85)) {
      bVar2 = gx8002_flash_read_status();
      bVar3 = gx8002_flash_read_status2();
      piVar6 = *(int **)(*(int *)(iVar4 + 0xc) + 0x10);
      for (iVar4 = 0; iVar4 != piVar6[1]; iVar4 = iVar4 + 1) {
        pbVar5 = (byte *)(iVar4 * 8 + *piVar6);
        iVar7 = *(int *)(pbVar5 + 4);
        if ((*pbVar5 == (bVar2 & pbVar5[1])) && (pbVar5[2] == (bVar3 & pbVar5[3])))
        goto LAB_1002393a;
      }
    }
  }
  iVar7 = -1;
LAB_1002393a:
  *param_1 = iVar7;
  return -(uint)(byte)~(iVar7 != -1);
}

