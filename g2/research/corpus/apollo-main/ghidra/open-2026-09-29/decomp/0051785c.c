
bool FUN_0051785c(float *param_1,float *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  
  fVar9 = param_1[3];
  fVar1 = param_1[1];
  fVar4 = param_2[1];
  fVar12 = *param_2;
  fVar2 = *param_1;
  fVar3 = param_1[2];
  iVar5 = (int)((fVar1 - fVar9) * fVar12 + (fVar9 - fVar4) * fVar2 + (fVar4 - fVar1) * fVar3);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar6 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  fVar7 = param_1[5];
  fVar8 = param_1[4];
  iVar5 = (int)((fVar9 - fVar7) * fVar12 + (fVar7 - fVar4) * fVar3 + (fVar4 - fVar9) * fVar8);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar10 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  fVar11 = param_1[7];
  fVar13 = param_1[6];
  iVar5 = (int)((fVar7 - fVar11) * fVar12 + (fVar11 - fVar4) * fVar8 + (fVar4 - fVar7) * fVar13);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar14 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar11 - fVar1) * fVar12 + (fVar1 - fVar4) * fVar13 + (fVar4 - fVar11) * fVar2);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar4 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar9 - fVar7) * fVar2 + (fVar7 - fVar1) * fVar3 + (fVar1 - fVar9) * fVar8);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar3 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  iVar5 = (int)((fVar11 - fVar1) * fVar8 + (fVar1 - fVar7) * fVar13 + (fVar7 - fVar11) * fVar2);
  if (iVar5 < 0) {
    iVar5 = -iVar5;
  }
  fVar1 = (float)VectorSignedFixedToFloat(iVar5,0x20,1);
  return (int)fVar4 + (int)fVar14 + (int)fVar10 + (int)fVar6 <= (int)fVar1 + (int)fVar3;
}

