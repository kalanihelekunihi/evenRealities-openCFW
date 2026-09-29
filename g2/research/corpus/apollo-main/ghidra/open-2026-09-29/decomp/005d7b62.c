
void FUN_005d7b62(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  
  iVar3 = *(int *)(param_1 + 0xc);
  uVar4 = *(uint *)(param_1 + 4);
  do {
    if (param_3 == 0) {
      return;
    }
    iVar1 = 0;
    iVar5 = *(int *)(param_2 + 0x1c);
    if (-1 < (int)((uint)*(byte *)(param_2 + 0x10) << 0x1b)) {
      if ((*(char *)(param_2 + 0x14) == param_5) || (*(char *)(param_2 + 0x14) + param_5 == 0)) {
        iVar1 = (int)*(char *)(param_2 + 0x14);
      }
      else if ((*(char *)(param_2 + 0x15) == param_5) || (*(char *)(param_2 + 0x15) + param_5 == 0))
      {
        iVar1 = (int)*(char *)(param_2 + 0x15);
      }
      if (iVar1 == 0) {
        if ((int)((uint)*(byte *)(param_2 + 0x10) << 0x19) < 0) {
          if (param_5 == 2) {
            uVar2 = 0x80;
            uVar7 = 0x100;
          }
          else {
            uVar2 = 0x100;
            uVar7 = 0x80;
          }
          if ((*(uint *)(param_2 + 0x10) & uVar2) == 0) {
            if ((*(uint *)(param_2 + 0x10) & uVar7) != 0) {
              for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1) {
                piVar6 = *(int **)(iVar3 + uVar2 * 4);
                iVar1 = (iVar5 - *piVar6) - piVar6[1];
                if ((iVar1 < param_4) && (-iVar1 < param_4)) {
                  *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x400;
                  *(int **)(param_2 + 0x18) = piVar6;
                  *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x10;
                  break;
                }
              }
            }
          }
          else {
            for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1) {
              piVar6 = *(int **)(iVar3 + uVar2 * 4);
              iVar1 = iVar5 - *piVar6;
              if ((iVar1 < param_4) && (-iVar1 < param_4)) {
                *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x200;
                *(int **)(param_2 + 0x18) = piVar6;
                *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x10;
                break;
              }
            }
          }
          if (*(int *)(param_2 + 0x18) == 0) {
            for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1) {
              piVar6 = *(int **)(iVar3 + uVar2 * 4);
              if ((*piVar6 <= iVar5) && (iVar5 <= piVar6[1] + *piVar6)) {
                *(int **)(param_2 + 0x18) = piVar6;
                break;
              }
            }
          }
        }
      }
      else if (iVar1 == param_5) {
        for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1) {
          piVar6 = *(int **)(iVar3 + uVar2 * 4);
          iVar1 = iVar5 - *piVar6;
          if ((iVar1 < param_4) && (-iVar1 < param_4)) {
            *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x10;
            *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x200;
            *(int **)(param_2 + 0x18) = piVar6;
            break;
          }
        }
      }
      else if (iVar1 + param_5 == 0) {
        for (uVar2 = 0; uVar2 < uVar4; uVar2 = uVar2 + 1) {
          piVar6 = *(int **)(iVar3 + uVar2 * 4);
          iVar1 = (iVar5 - *piVar6) - piVar6[1];
          if ((iVar1 < param_4) && (-iVar1 < param_4)) {
            *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x10;
            *(uint *)(param_2 + 0x10) = *(uint *)(param_2 + 0x10) | 0x400;
            *(int **)(param_2 + 0x18) = piVar6;
            break;
          }
        }
      }
    }
    param_3 = param_3 + -1;
    param_2 = param_2 + 0x28;
  } while( true );
}

