
void FUN_005128a0(void)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  float *pfVar4;
  int iVar5;
  uint in_fpscr;
  float fVar6;
  
  piVar2 = DAT_00512c34;
  iVar5 = osKernelGetTickCount();
  *piVar2 = iVar5;
  piVar3 = DAT_00512c38;
  piVar1 = DAT_00512c30;
  *DAT_00512c38 = *piVar2 - *DAT_00512c30;
  *piVar1 = *piVar2;
  pfVar4 = DAT_00512c3c;
  fVar6 = (float)VectorUnsignedToFloat(*piVar3,(byte)(in_fpscr >> 0x16) & 3);
  *DAT_00512c3c = fVar6 / DAT_00512a64;
  if (DAT_00512b10 <= *pfVar4) {
    FUN_0051201c(*pfVar4);
  }
  return;
}

