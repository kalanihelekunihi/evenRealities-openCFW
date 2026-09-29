
void FUN_005d7a6c(uint *param_1)

{
  uint uVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  
  uVar1 = 0;
  do {
    if (param_1[1] <= uVar1) {
      uVar1 = 0;
      goto LAB_005d7aec;
    }
    piVar2 = *(int **)(param_1[3] + uVar1 * 8);
    piVar5 = piVar2;
    if (*(int *)(param_1[3] + uVar1 * 8 + 4) != 0) {
      do {
        piVar5 = (int *)*piVar5;
        if (piVar5 == piVar2) goto LAB_005d7b5a;
      } while (piVar5[7] == piVar2[7]);
      piVar3 = (int *)piVar5[1];
      piVar2 = piVar3;
      piVar4 = piVar3;
      while (piVar2 = (int *)piVar2[1], piVar2 != piVar3) {
        if (piVar2[7] != piVar4[7]) {
          if (*(int *)((int)piVar5 + 0x1c) < piVar4[7]) {
            if (piVar2[7] < piVar4[7]) {
LAB_005d7ab2:
              do {
                piVar4[4] = piVar4[4] | 0x40;
                piVar4 = (int *)piVar4[1];
              } while (piVar4 != piVar2);
            }
          }
          else if (piVar4[7] < piVar2[7]) goto LAB_005d7ab2;
          piVar5 = (int *)*piVar2;
          piVar4 = piVar2;
        }
      }
    }
    uVar1 = uVar1 + 1;
  } while( true );
LAB_005d7b5a:
  uVar1 = uVar1 + 1;
LAB_005d7aec:
  if (*param_1 <= uVar1) {
    return;
  }
  piVar4 = (int *)(param_1[2] + uVar1 * 0x28);
  piVar5 = piVar4;
  piVar2 = piVar4;
  if ((int)((uint)*(byte *)(piVar4 + 4) << 0x19) < 0) {
    do {
      piVar5 = (int *)*piVar5;
      if (piVar5 == piVar4) goto LAB_005d7b5a;
    } while (piVar5[8] == piVar4[8]);
    do {
      piVar2 = (int *)piVar2[1];
      if (piVar2 == piVar4) goto LAB_005d7b5a;
    } while (piVar2[8] == piVar4[8]);
  }
  if ((piVar5[8] < piVar4[8]) && (piVar4[8] < piVar2[8])) {
    piVar4[4] = piVar4[4] | 0x80;
  }
  else if ((piVar4[8] < piVar5[8]) && (piVar2[8] < piVar4[8])) {
    piVar4[4] = piVar4[4] | 0x100;
  }
  goto LAB_005d7b5a;
}

