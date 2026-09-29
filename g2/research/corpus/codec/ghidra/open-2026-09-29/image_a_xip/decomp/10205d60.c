
undefined4 gx8002_snpu_run_task(int *param_1,int param_2,int param_3)

{
  uint uVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  piVar2 = piRam10205e20;
  if (((param_1 == (int *)0x0) || (piRam10205e20[0x171] == 0)) ||
     ((piRam10205e20[0x16d] + 1) % 10 == piRam10205e20[0x16c])) {
    uVar3 = 0xffffffff;
  }
  else {
    iVar6 = piRam10205e20[0x16d];
    piRam10205e20[iVar6 * 0x24 + 0x24] = param_2;
    iVar4 = *param_1;
    piVar2[iVar6 * 0x24 + 0x26] = param_3;
    piVar2[iVar6 * 0x24 + 10] = param_1[1];
    piVar2[iVar6 * 0x24 + 0xd] = param_1[2];
    piVar2[iVar6 * 0x24 + 0x25] = iVar4;
    iVar5 = param_1[3];
    iVar4 = param_1[5];
    piVar2[iVar6 * 0x24 + 0x10] = iVar4;
    piVar2[iVar6 * 0x24 + 0x13] = iVar5;
    piVar2[iVar6 * 0x24 + 0x16] = param_1[4];
    piVar2[iVar6 * 0x24 + 0x19] = param_1[6];
    piVar2[iVar6 * 0x24 + 0x1c] = param_1[7];
    uVar1 = (uint)(piVar2 + iVar6 * 0x24 + 4) & 0x7ffffff;
    piVar2[iVar6 * 0x24 + 0x1f] = uVar1;
    piVar2[iVar6 * 0x24 + 0x22] = -2;
    piVar2[iVar6 * 0x24 + 4] = iRam10205e24;
    piVar2[iVar6 * 0x24 + 5] = uVar1;
    piVar2[iVar6 * 0x24 + 0x21] = iVar4;
    piVar2[0x16d] = (piVar2[0x16d] + 1) % 10;
    if (*piVar2 == 2) {
      gx8002_snpu_resume_internal();
    }
    gx8002_snpu_submit_task(piVar2 + iVar6 * 0x24 + 4);
    uVar3 = 0;
  }
  return uVar3;
}

