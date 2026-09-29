
void FUN_005d7e1a(int *param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  
  iVar3 = param_2[2];
  for (iVar2 = *param_2; iVar2 != 0; iVar2 = iVar2 + -1) {
    if (((((*(char *)(iVar3 + 0x14) == '\x02') || (*(char *)(iVar3 + 0x14) == -2)) ||
         (*(char *)(iVar3 + 0x15) == '\x02')) || (*(char *)(iVar3 + 0x15) == -2)) &&
       (-1 < (int)((uint)*(byte *)(iVar3 + 0x10) << 0x1b))) {
      iVar4 = *(int *)(iVar3 + 0x1c);
      iVar1 = *param_1;
      piVar5 = param_1 + 1;
      while ((iVar1 != 0 &&
             (iVar6 = iVar4 - piVar5[3], iVar6 + param_1[0x207] < 0 == SCARRY4(iVar6,param_1[0x207])
             ))) {
        if ((iVar4 <= param_1[0x207] + piVar5[2]) &&
           (((char)param_1[0x208] != '\0' || (iVar6 <= param_1[0x206])))) {
          *(int *)(iVar3 + 0x24) = piVar5[6];
          *(uint *)(iVar3 + 0x10) = *(uint *)(iVar3 + 0x10) | 0x10;
          *(uint *)(iVar3 + 0x10) = *(uint *)(iVar3 + 0x10) | 0x20;
        }
        iVar1 = iVar1 + -1;
        piVar5 = piVar5 + 8;
      }
      iVar1 = param_1[0x81];
      piVar5 = param_1 + 0x81 + iVar1 * 8 + -7;
      while ((iVar1 != 0 &&
             (iVar6 = piVar5[2] - iVar4, iVar6 + param_1[0x207] < 0 == SCARRY4(iVar6,param_1[0x207])
             ))) {
        if ((piVar5[3] - param_1[0x207] <= iVar4) &&
           (((char)param_1[0x208] != '\0' || (iVar6 < param_1[0x206])))) {
          *(int *)(iVar3 + 0x24) = piVar5[7];
          *(uint *)(iVar3 + 0x10) = *(uint *)(iVar3 + 0x10) | 0x10;
          *(uint *)(iVar3 + 0x10) = *(uint *)(iVar3 + 0x10) | 0x20;
        }
        iVar1 = iVar1 + -1;
        piVar5 = piVar5 + -8;
      }
    }
    iVar3 = iVar3 + 0x28;
  }
  return;
}

