
int FUN_00568e52(int *param_1,int *param_2,int *param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  int *piVar9;
  int *piVar10;
  int local_17c;
  int local_178;
  int local_174;
  int local_170;
  int *local_16c;
  int local_168;
  int local_164;
  int local_160;
  int local_15c;
  int local_158;
  int local_154;
  undefined4 local_150;
  int local_14c;
  int local_148;
  undefined4 local_144;
  int local_140;
  int *local_13c;
  int local_138 [60];
  int aiStack_48 [8];
  undefined4 uStack_28;
  
  iVar8 = 0;
  local_13c = aiStack_48;
  bVar1 = true;
  if (((param_1 == (int *)0x0) || (param_2 == (int *)0x0)) || (param_3 == (int *)0x0)) {
    iVar8 = 6;
  }
  else if ((((param_1[2] - *param_2) + 1U < 3) && ((param_1[3] - param_2[1]) + 1U < 3)) &&
          (((*param_2 - *param_3) + 1U < 3 && ((param_2[1] - param_3[1]) + 1U < 3)))) {
    iVar7 = param_3[1];
    param_1[2] = *param_3;
    param_1[3] = iVar7;
  }
  else {
    piVar9 = local_138;
    local_138[0] = *param_3;
    local_138[1] = param_3[1];
    local_138[2] = *param_2;
    local_138[3] = param_2[1];
    local_138[4] = param_1[2];
    local_138[5] = param_1[3];
    local_16c = param_3;
    uStack_28 = param_4;
    while (local_138 <= piVar9) {
      local_17c = *param_1;
      local_170 = local_17c;
      if ((piVar9 < local_13c) && (iVar7 = FUN_00568020(piVar9,&local_17c,&local_170), iVar7 == 0))
      {
        if ((char)param_1[5] != '\0') {
          *param_1 = local_17c;
        }
        FUN_00567fce(piVar9);
        piVar9 = piVar9 + 4;
      }
      else {
        if (bVar1) {
          bVar1 = false;
          if ((char)param_1[5] == '\0') {
            param_1[1] = local_17c;
            iVar8 = FUN_00568ce2(param_1,0);
          }
          else {
            iVar8 = FUN_00568d2a(param_1,local_17c,0);
          }
        }
        else {
          FT_Angle_Diff(*param_1,local_17c);
          iVar7 = FUN_00567fc6();
          if (DAT_00569a34 <= iVar7) {
            iVar8 = piVar9[5];
            param_1[2] = piVar9[4];
            param_1[3] = iVar8;
            param_1[1] = local_17c;
            *(undefined1 *)((int)param_1 + 0x2a) = 0;
            iVar8 = FUN_00568ce2(param_1,0);
            *(undefined1 *)((int)param_1 + 0x2a) = *(undefined1 *)((int)param_1 + 0x2b);
          }
        }
        if (iVar8 != 0) {
          return iVar8;
        }
        local_150 = 0;
        iVar7 = FT_Angle_Diff(local_17c,local_170);
        local_140 = iVar7 / 2 + local_17c;
        uVar2 = FT_Cos();
        local_144 = FT_DivFix(param_1[0xc],uVar2);
        if ((char)param_1[10] != '\0') {
          local_150 = FT_Atan2(*piVar9 - piVar9[4],piVar9[1] - piVar9[5]);
        }
        piVar10 = param_1 + 0xd;
        for (iVar7 = 0; iVar7 < 2; iVar7 = iVar7 + 1) {
          FT_Vector_From_Polar
                    (&local_160,local_144,(int)&DAT_005a0000 + local_140 + iVar7 * -0xb40000);
          local_160 = piVar9[2] + local_160;
          local_15c = piVar9[3] + local_15c;
          FT_Vector_From_Polar
                    (&local_178,param_1[0xc],(int)&DAT_005a0000 + local_170 + iVar7 * -0xb40000);
          local_178 = *piVar9 + local_178;
          local_174 = piVar9[1] + local_174;
          if ((char)param_1[10] == '\0') {
LAB_0056912a:
            iVar8 = FUN_0056847a(piVar10,&local_160,&local_178);
          }
          else {
            iVar8 = piVar10[2] + *piVar10 * 8;
            local_168 = *(int *)(iVar8 + -8);
            local_164 = *(int *)(iVar8 + -4);
            iVar8 = FT_Atan2(local_178 - local_168,local_174 - local_164);
            FT_Angle_Diff(local_150,iVar8);
            iVar3 = FUN_00567fc6();
            if (iVar3 < DAT_0056915c) goto LAB_0056912a;
            iVar3 = FT_Atan2(piVar9[4] - local_168,piVar9[5] - local_164);
            iVar4 = FT_Atan2(*piVar9 - local_178,piVar9[1] - local_174);
            local_14c = local_178 - local_168;
            local_148 = local_174 - local_164;
            uVar2 = FT_Vector_Length(&local_14c);
            FT_Sin(iVar8 - iVar4);
            uVar5 = FUN_00567fc6();
            FT_Sin(iVar3 - iVar4);
            uVar6 = FUN_00567fc6();
            uVar2 = FT_MulDiv(uVar2,uVar5,uVar6);
            FT_Vector_From_Polar(&local_158,uVar2,iVar3);
            local_158 = local_168 + local_158;
            local_154 = local_164 + local_154;
            *(undefined1 *)(piVar10 + 4) = 0;
            iVar8 = FUN_005683f2(piVar10,&local_158,0);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_005683f2(piVar10,&local_178,0);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_0056847a(piVar10,&local_160,&local_168);
            if (iVar8 != 0) {
              return iVar8;
            }
            iVar8 = FUN_005683f2(piVar10,&local_178,0);
          }
          if (iVar8 != 0) {
            return iVar8;
          }
          piVar10 = piVar10 + 8;
          iVar8 = 0;
        }
        piVar9 = piVar9 + -4;
        *param_1 = local_170;
      }
    }
    iVar7 = local_16c[1];
    param_1[2] = *local_16c;
    param_1[3] = iVar7;
  }
  return iVar8;
}

