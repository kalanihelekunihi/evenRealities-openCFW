
undefined8 FUN_00472ef6(float param_1,int *param_2,int param_3,float param_4,uint param_5)

{
  int iVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int *piVar9;
  
  iVar8 = *param_2;
  if (iVar8 < 4) {
    iVar8 = -3;
    param_1 = param_4;
  }
  else if (param_1 == 0.0) {
    *param_2 = DAT_00473464;
    iVar8 = 3;
    param_1 = param_4;
  }
  else {
    uVar3 = (uint)ABS(param_1) >> 0x17;
    iVar4 = uVar3 - 0x7f;
    uVar5 = (uint)param_1 & 0xffffff | 0x800000;
    uVar7 = 0;
    iVar1 = 0;
    if (iVar4 < 0x1f) {
      if (iVar4 < -0x17) {
        iVar8 = -1;
      }
      else {
        uVar6 = param_5;
        if (iVar4 < 0x17) {
          if (iVar4 < 0) {
            uVar7 = (int)((uint)param_1 & 0xffffff | 0x800000) >> (-(uVar3 - 0x7e) & 0xff);
          }
          else {
            iVar1 = (int)uVar5 >> (0x17U - iVar4 & 0xff);
            uVar7 = uVar5 << (uVar3 - 0x7e & 0xff) & 0xffffff;
            uVar6 = 0x17U - iVar4;
          }
        }
        else {
          iVar1 = uVar5 << (uVar3 - 0x96 & 0xff);
        }
        piVar9 = param_2;
        if ((int)param_1 < 0) {
          *(char *)param_2 = '-';
          piVar9 = (int *)((int)param_2 + 1);
        }
        if (iVar1 == 0) {
          *(char *)piVar9 = '0';
          piVar9 = (int *)((int)piVar9 + 1);
        }
        else {
          if (iVar1 < 1) {
            *(char *)piVar9 = '-';
            piVar9 = (int *)((int)piVar9 + 1);
            FUN_00472de0(-iVar1,-iVar1 >> 0x1f,piVar9,uVar6,param_1,param_5);
          }
          else {
            FUN_00472de0(iVar1,iVar1 >> 0x1f,piVar9,uVar6,param_1,param_5);
          }
          for (; (char)*piVar9 != '\0'; piVar9 = (int *)((int)piVar9 + 1)) {
          }
        }
        *(char *)piVar9 = '.';
        piVar2 = (int *)((int)piVar9 + 1);
        if (uVar7 == 0) {
          *(char *)piVar2 = '0';
          piVar2 = (int *)((int)piVar9 + 2);
        }
        else {
          iVar8 = (iVar8 - ((int)piVar2 - (int)param_2)) + -1;
          if (iVar8 <= param_3) {
            param_3 = iVar8;
          }
          for (iVar8 = 0; iVar8 < param_3; iVar8 = iVar8 + 1) {
            *(char *)piVar2 = (char)(uVar7 * 10 >> 0x18) + '0';
            piVar2 = (int *)((int)piVar2 + 1);
            uVar7 = uVar7 * 10 & 0xffffff;
          }
          piVar9 = piVar2;
          if (4 < (int)(uVar7 * 10) >> 0x18) {
            while (piVar9 = (int *)((int)piVar9 + -1), param_2 <= piVar9) {
              if (*(char *)piVar9 != '.') {
                if (*(char *)piVar9 != '9') {
                  *(char *)piVar9 = *(char *)piVar9 + '\x01';
                  break;
                }
                *(char *)piVar9 = '0';
              }
            }
          }
        }
        *(char *)piVar2 = '\0';
        iVar8 = (int)piVar2 - (int)param_2;
      }
    }
    else {
      iVar8 = -2;
    }
  }
  return CONCAT44(param_1,iVar8);
}

