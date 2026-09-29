
float * gx8002_kws_strategy(int param_1)

{
  undefined *puVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  float fVar5;
  float fVar6;
  float *pfVar7;
  float *pfVar8;
  float fVar9;
  int iVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  
  puVar1 = PTR_s__ST__Kws__s__d__th__d_S__d_D__d_10208b50;
  fVar9 = fRam10208b4c;
  piVar4 = piRam10208b48;
  pfVar7 = (float *)0x0;
  if (*piRam10208b48 != 0) {
    fVar13 = 0.0;
    fVar5 = 0.0;
    pfVar7 = (float *)(piRam10208b48 + 1);
    fVar6 = 0.0;
    pfVar8 = pfVar7;
    for (iVar10 = 0; iVar10 < *piVar4; iVar10 = iVar10 + 1) {
      fVar11 = *pfVar8;
      fVar14 = *pfVar8;
      iVar2 = func_0x100264dc();
      if (iVar2 == 0) {
        piVar3 = (int *)0x0;
      }
      else {
        piVar3 = (int *)(*(int *)(iVar2 + 4) + (int)fVar11 * 0x58);
      }
      fVar11 = (float)*piVar3 / fVar5;
      if (fVar11 <= fVar14) {
        fVar12 = fVar14 - fVar11;
      }
      else {
        fVar12 = (fVar14 - (fVar11 - fVar5)) * fVar6;
        if (fVar12 < 0.0) {
          fVar12 = fVar9;
        }
      }
      if (fVar13 < fVar12) {
        pfVar7 = pfVar8;
        fVar13 = fVar12;
      }
      gx8002_printf(puVar1,piVar3,piVar3[0x14],(int)(fVar11 * fVar5),(int)(fVar14 * fVar5));
      pfVar8 = pfVar8 + 5;
    }
    fVar9 = *pfVar7;
    iVar10 = func_0x100264dc();
    if (iVar10 == 0) {
      piVar4 = (int *)0x0;
    }
    else {
      piVar4 = (int *)(*(int *)(iVar10 + 4) + (int)fVar9 * 0x58);
    }
    gx8002_printf(PTR_s__ST__Activation_ctx__d_Kws__s__d_10208b54,*(undefined4 *)(param_1 + 8),
                  piVar4,piVar4[0x14],(int)(((float)*piVar4 / fVar5) * fVar5));
  }
  return pfVar7;
}

