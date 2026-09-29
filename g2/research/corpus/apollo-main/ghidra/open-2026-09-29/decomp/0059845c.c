
/* WARNING: Instruction at (ram,0x005988ce) overlaps instruction at (ram,0x005988cc)
    */

float * FUN_0059845c(float *param_1,int param_2,undefined4 param_3,float *param_4)

{
  uint uVar1;
  float *pfVar2;
  int iVar3;
  float *pfVar4;
  float *pfVar5;
  float *pfVar6;
  float *pfVar7;
  int *piVar8;
  float *pfVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  uint local_6c;
  float *local_68 [2];
  uint local_60;
  int local_5c;
  int local_58;
  float *local_54;
  float *local_50;
  float *local_4c;
  int *local_48;
  int local_44;
  
  iVar3 = (int)((ulonglong)((longlong)param_2 * (longlong)DAT_00598dcc) >> 0x20);
  local_68[0] = param_4;
  local_6c = (iVar3 >> 1) - (iVar3 >> 0x1f);
  local_68[1] = (float *)param_3;
  local_60 = 0;
  if (0 < (int)local_6c) {
    pfVar4 = param_1 + local_6c * 2;
    pfVar2 = param_1 + local_6c * 8;
    pfVar6 = param_1 + local_6c * 4;
    pfVar7 = param_1 + local_6c * 6;
    do {
      fVar10 = pfVar4[1] + pfVar2[1];
      fVar16 = pfVar4[1] - pfVar2[1];
      fVar15 = *pfVar6 + *pfVar7;
      fVar14 = *pfVar6 - *pfVar7;
      fVar12 = *pfVar4 + *pfVar2;
      fVar11 = *pfVar4 - *pfVar2;
      fVar13 = pfVar6[1] + pfVar7[1];
      fVar19 = pfVar6[1] - pfVar7[1];
      *param_4 = *param_1 + fVar12 + fVar15;
      param_4[1] = param_1[1] + fVar10 + fVar13;
      fVar18 = fVar16 * DAT_00598648;
      fVar17 = fVar19 * DAT_00598640;
      param_4[2] = (((fVar12 * DAT_0059864c + *param_1) - fVar18) + fVar15 * DAT_00598644) - fVar17;
      fVar21 = fVar11 * DAT_00598648;
      fVar20 = fVar14 * DAT_00598640;
      param_4[3] = fVar10 * DAT_0059864c + param_1[1] + fVar21 + fVar13 * DAT_00598644 + fVar20;
      fVar16 = fVar16 * DAT_00598640;
      fVar19 = fVar19 * DAT_00598648;
      param_4[4] = ((fVar12 * DAT_00598644 + *param_1) - fVar16) + fVar15 * DAT_0059864c + fVar19;
      fVar11 = fVar11 * DAT_00598640;
      fVar14 = fVar14 * DAT_00598648;
      param_4[5] = (fVar10 * DAT_00598644 + param_1[1] + fVar11 + fVar13 * DAT_0059864c) - fVar14;
      param_4[6] = (fVar12 * DAT_00598644 + *param_1 + fVar16 + fVar15 * DAT_0059864c) - fVar19;
      param_4[7] = ((fVar10 * DAT_00598644 + param_1[1]) - fVar11) + fVar13 * DAT_0059864c + fVar14;
      param_4[8] = fVar12 * DAT_0059864c + *param_1 + fVar18 + fVar15 * DAT_00598644 + fVar17;
      param_4[9] = (((fVar10 * DAT_0059864c + param_1[1]) - fVar21) + fVar13 * DAT_00598644) -
                   fVar20;
      param_1 = param_1 + 2;
      param_4 = param_4 + 10;
      pfVar7 = pfVar7 + 2;
      pfVar6 = pfVar6 + 2;
      pfVar2 = pfVar2 + 2;
      pfVar4 = pfVar4 + 2;
      loopEnd();
    } while( true );
  }
  local_44 = 0;
  if ((local_6c & local_6c - 1) != 0) {
    local_60 = 0;
    local_44 = 0;
    local_48 = DAT_00598dd0;
    do {
      iVar3 = (int)((ulonglong)((longlong)(int)local_6c * (longlong)DAT_00598dd4) >> 0x20);
      local_6c = iVar3 - (iVar3 >> 0x1f);
      local_5c = *(int *)*local_48;
      local_4c = (float *)((int *)*local_48)[1];
      local_50 = local_68[local_60];
      local_54 = local_50 + local_5c * local_6c * 2;
      pfVar7 = local_54 + local_5c * local_6c * 2;
      pfVar4 = local_68[local_60 ^ 1];
      pfVar2 = pfVar4 + local_5c * 2;
      pfVar6 = pfVar2 + local_5c * 2;
      if (0 < (int)local_6c) {
        local_58 = local_5c * 0x18;
        uVar1 = local_6c;
        do {
          if (0 < local_5c) {
            pfVar9 = local_4c + local_5c * 4;
            pfVar5 = local_4c + local_5c * 8;
            do {
              *pfVar4 = (((*local_50 + *local_54 * *local_4c) - local_54[1] * local_4c[1]) +
                        *pfVar7 * local_4c[2]) - pfVar7[1] * local_4c[3];
              pfVar4[1] = local_50[1] + local_54[1] * *local_4c + *local_54 * local_4c[1] +
                          pfVar7[1] * local_4c[2] + *pfVar7 * local_4c[3];
              *pfVar2 = (((*local_50 + *local_54 * *pfVar9) - local_54[1] * pfVar9[1]) +
                        *pfVar7 * pfVar9[2]) - pfVar7[1] * pfVar9[3];
              pfVar2[1] = local_50[1] + local_54[1] * *pfVar9 + *local_54 * pfVar9[1] +
                          pfVar7[1] * pfVar9[2] + *pfVar7 * pfVar9[3];
              *pfVar6 = (((*local_50 + *local_54 * *pfVar5) - local_54[1] * pfVar5[1]) +
                        *pfVar7 * pfVar5[2]) - pfVar7[1] * pfVar5[3];
              pfVar6[1] = local_50[1] + local_54[1] * *pfVar5 + *local_54 * pfVar5[1] +
                          pfVar7[1] * pfVar5[2] + *pfVar7 * pfVar5[3];
              local_50 = local_50 + 2;
              local_54 = local_54 + 2;
              pfVar7 = pfVar7 + 2;
              pfVar5 = pfVar5 + 4;
              pfVar9 = pfVar9 + 4;
              local_4c = local_4c + 4;
              pfVar6 = pfVar6 + 2;
              pfVar2 = pfVar2 + 2;
              pfVar4 = pfVar4 + 2;
              loopEnd();
            } while( true );
          }
          uVar1 = uVar1 - 1;
          pfVar4 = pfVar4 + local_5c * 6;
          pfVar2 = pfVar2 + local_5c * 6;
          pfVar6 = pfVar6 + local_5c * 6;
        } while (uVar1 != 0);
      }
      local_44 = local_44 + 1;
      local_60 = local_60 ^ 1;
      local_48 = local_48 + 1;
    } while ((local_6c & local_6c - 1) != 0);
  }
  piVar8 = (int *)(DAT_00598dd8 + local_44 * 4);
  do {
    if ((int)local_6c < 2) {
      return local_68[local_60];
    }
    iVar3 = *(int *)*piVar8;
    local_6c = (int)local_6c >> 1;
    pfVar6 = (float *)((int *)*piVar8)[1];
    pfVar9 = local_68[local_60];
    pfVar7 = pfVar9 + iVar3 * local_6c * 2;
    pfVar4 = local_68[local_60 ^ 1];
    pfVar2 = pfVar4 + iVar3 * 2;
    uVar1 = local_6c;
    if (0 < (int)local_6c) {
      do {
        if (0 < iVar3) {
          do {
            *pfVar4 = (*pfVar9 + *pfVar7 * *pfVar6) - pfVar7[1] * pfVar6[1];
            pfVar4[1] = pfVar9[1] + pfVar7[1] * *pfVar6 + *pfVar7 * pfVar6[1];
            *pfVar2 = (*pfVar9 - *pfVar7 * *pfVar6) + pfVar7[1] * pfVar6[1];
            pfVar2[1] = (pfVar9[1] - pfVar7[1] * *pfVar6) - *pfVar7 * pfVar6[1];
            pfVar9 = pfVar9 + 2;
            pfVar7 = pfVar7 + 2;
            loopEnd();
          } while( true );
        }
        uVar1 = uVar1 - 1;
        pfVar4 = pfVar4 + iVar3 * 4;
        pfVar2 = pfVar2 + iVar3 * 4;
      } while (uVar1 != 0);
    }
    local_60 = local_60 ^ 1;
    piVar8 = piVar8 + 3;
  } while( true );
}

