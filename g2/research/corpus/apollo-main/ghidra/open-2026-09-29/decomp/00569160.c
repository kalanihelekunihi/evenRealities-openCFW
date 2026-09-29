
int FUN_00569160(int *param_1,int *param_2,int *param_3,int *param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int *piVar10;
  int local_1a4;
  int local_1a0;
  int local_19c;
  int local_198;
  int local_194;
  int *local_190;
  int local_18c;
  int local_188;
  int local_184;
  int local_180;
  int local_17c;
  int local_178;
  int local_174;
  int local_170;
  undefined4 local_16c;
  int local_168;
  int local_164;
  undefined4 local_160;
  undefined4 local_15c;
  int local_158;
  int local_154;
  int *local_150;
  int local_14c;
  int local_148;
  int local_144;
  int local_140;
  int local_13c;
  int local_138;
  int local_134;
  int local_130;
  int aiStack_4c [10];
  
  iVar8 = 0;
  local_150 = aiStack_4c;
  bVar1 = true;
  if ((((param_1 == (int *)0x0) || (param_2 == (int *)0x0)) || (param_3 == (int *)0x0)) ||
     (param_4 == (int *)0x0)) {
    iVar8 = 6;
  }
  else if (((((param_1[2] - *param_2) + 1U < 3) && ((param_1[3] - param_2[1]) + 1U < 3)) &&
           (((*param_2 - *param_3) + 1U < 3 &&
            (((param_2[1] - param_3[1]) + 1U < 3 && ((*param_3 - *param_4) + 1U < 3)))))) &&
          ((param_3[1] - param_4[1]) + 1U < 3)) {
    iVar7 = param_4[1];
    param_1[2] = *param_4;
    param_1[3] = iVar7;
  }
  else {
    piVar9 = &local_14c;
    local_14c = *param_4;
    local_148 = param_4[1];
    local_144 = *param_3;
    local_140 = param_3[1];
    local_13c = *param_2;
    local_138 = param_2[1];
    local_134 = param_1[2];
    local_130 = param_1[3];
    local_190 = param_4;
    while (&local_14c <= piVar9) {
      local_1a4 = *param_1;
      local_198 = local_1a4;
      local_194 = local_1a4;
      if ((piVar9 < local_150) &&
         (iVar7 = FUN_00568176(piVar9,&local_1a4,&local_194,&local_198), iVar7 == 0)) {
        if ((char)param_1[5] != '\0') {
          *param_1 = local_1a4;
        }
        FUN_005680ce(piVar9);
        piVar9 = piVar9 + 6;
      }
      else {
        if (bVar1) {
          bVar1 = false;
          if ((char)param_1[5] == '\0') {
            param_1[1] = local_1a4;
            iVar8 = FUN_00568ce2(param_1,0);
          }
          else {
            iVar8 = FUN_00568d2a(param_1,local_1a4,0);
          }
        }
        else {
          FT_Angle_Diff(*param_1,local_1a4);
          iVar7 = FUN_00567fc6();
          if (DAT_00569a38 <= iVar7) {
            iVar8 = piVar9[7];
            param_1[2] = piVar9[6];
            param_1[3] = iVar8;
            param_1[1] = local_1a4;
            *(undefined1 *)((int)param_1 + 0x2a) = 0;
            iVar8 = FUN_00568ce2(param_1,0);
            *(undefined1 *)((int)param_1 + 0x2a) = *(undefined1 *)((int)param_1 + 0x2b);
          }
        }
        if (iVar8 != 0) {
          return iVar8;
        }
        local_16c = 0;
        iVar7 = FT_Angle_Diff(local_1a4,local_194);
        iVar2 = FT_Angle_Diff(local_194,local_198);
        local_154 = FUN_00568160(local_1a4,local_194);
        local_158 = FUN_00568160(local_194,local_198);
        uVar3 = FT_Cos(iVar7 / 2);
        local_15c = FT_DivFix(param_1[0xc],uVar3);
        uVar3 = FT_Cos(iVar2 / 2);
        local_160 = FT_DivFix(param_1[0xc],uVar3);
        if ((char)param_1[10] != '\0') {
          local_16c = FT_Atan2(*piVar9 - piVar9[6],piVar9[1] - piVar9[7]);
        }
        piVar10 = param_1 + 0xd;
        for (iVar7 = 0; iVar7 < 2; iVar7 = iVar7 + 1) {
          FT_Vector_From_Polar
                    (&local_17c,local_15c,(int)&DAT_005a0000 + local_154 + iVar7 * -0xb40000);
          local_17c = piVar9[4] + local_17c;
          local_178 = piVar9[5] + local_178;
          FT_Vector_From_Polar
                    (&local_184,local_160,(int)&DAT_005a0000 + local_158 + iVar7 * -0xb40000);
          local_184 = piVar9[2] + local_184;
          local_180 = piVar9[3] + local_180;
          FT_Vector_From_Polar
                    (&local_1a0,param_1[0xc],(int)&DAT_005a0000 + local_198 + iVar7 * -0xb40000);
          local_1a0 = *piVar9 + local_1a0;
          local_19c = piVar9[1] + local_19c;
          if ((char)param_1[10] == '\0') {
LAB_005694ac:
            iVar8 = FUN_005684c2(piVar10,&local_17c,&local_184,&local_1a0);
          }
          else {
            iVar8 = piVar10[2] + *piVar10 * 8;
            local_18c = *(int *)(iVar8 + -8);
            local_188 = *(int *)(iVar8 + -4);
            iVar8 = FT_Atan2(local_1a0 - local_18c,local_19c - local_188);
            FT_Angle_Diff(local_16c,iVar8);
            iVar2 = FUN_00567fc6();
            if (iVar2 < DAT_00569a3c) goto LAB_005694ac;
            iVar2 = FT_Atan2(piVar9[6] - local_18c,piVar9[7] - local_188);
            iVar4 = FT_Atan2(*piVar9 - local_1a0,piVar9[1] - local_19c);
            local_168 = local_1a0 - local_18c;
            local_164 = local_19c - local_188;
            uVar3 = FT_Vector_Length(&local_168);
            FT_Sin(iVar8 - iVar4);
            uVar5 = FUN_00567fc6();
            FT_Sin(iVar2 - iVar4);
            uVar6 = FUN_00567fc6();
            uVar3 = FT_MulDiv(uVar3,uVar5,uVar6);
            FT_Vector_From_Polar(&local_174,uVar3,iVar2);
            local_174 = local_18c + local_174;
            local_170 = local_188 + local_170;
            *(undefined1 *)(piVar10 + 4) = 0;
            iVar8 = FUN_005683f2(piVar10,&local_174,0);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_005683f2(piVar10,&local_1a0,0);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_005684c2(piVar10,&local_184,&local_17c,&local_18c);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_005683f2(piVar10,&local_1a0,0);
          }
          if (iVar8 != 0) {
            return iVar8;
          }
          piVar10 = piVar10 + 8;
          iVar8 = 0;
        }
        piVar9 = piVar9 + -6;
        *param_1 = local_198;
      }
    }
    iVar7 = local_190[1];
    param_1[2] = *local_190;
    param_1[3] = iVar7;
  }
  return iVar8;
}

