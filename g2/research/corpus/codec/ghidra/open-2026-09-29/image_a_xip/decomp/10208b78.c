
undefined4 gx8002_bionic_run(int *param_1)

{
  float *pfVar1;
  int *piVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = *(int *)(*param_1 + 0x1c);
  iVar5 = *(int *)(*param_1 + 0x24);
  piVar2 = (int *)func_0x100264dc();
  pfVar1 = pfRam10208bec;
  iVar4 = *piVar2;
  fVar3 = pfRam10208bec[3];
  pfRam10208bec[3] = (float)((int)fVar3 + 1);
  if (((int)((uint)(iVar4 * 1000000) >> 2) < ((int)fVar3 + 1) * iVar5 * iVar6) && (*pfVar1 < 0.0)) {
    pfVar1[3] = 0.0;
    fVar3 = *pfVar1 + 0.0;
    if (fVar3 <= 0.0) {
      *pfVar1 = fVar3;
    }
    else {
      *pfVar1 = 0.0;
    }
    gx8002_printf(uRam10208bf0,(int)*pfVar1);
  }
  return 0;
}

