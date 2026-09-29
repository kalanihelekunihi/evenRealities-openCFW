
uint pvPortMalloc(uint param_1)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  uint uVar5;
  int *piVar6;
  uint uVar7;
  uint uVar8;
  
  uVar8 = 0;
  FUN_0800c380();
  piVar1 = DAT_0800b49c;
  if (*DAT_0800b49c == 0) {
    FUN_0800ae0c();
  }
  if ((param_1 & piVar1[5]) == 0) {
    uVar7 = param_1;
    if (((param_1 != 0) && (uVar7 = param_1 + 8, (param_1 & 7) != 0)) &&
       (uVar7 = (8 - (param_1 & 7)) + uVar7, (uVar7 & 7) != 0)) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if ((uVar7 != 0) && (uVar7 <= (uint)piVar1[1])) {
      piVar2 = DAT_0800b4a0;
      piVar3 = (int *)*DAT_0800b4a0;
      do {
        piVar6 = piVar3;
        piVar4 = piVar2;
        if (uVar7 <= (uint)piVar6[1]) break;
        piVar2 = piVar6;
        piVar3 = (int *)*piVar6;
      } while ((int *)*piVar6 != (int *)0x0);
      if (piVar6 != (int *)*piVar1) {
        uVar8 = *piVar4 + 8;
        *piVar4 = *piVar6;
        if (0x10 < piVar6[1] - uVar7) {
          if (((int)piVar6 + uVar7 & 7) != 0) {
            disableIRQinterrupts();
            do {
                    /* WARNING: Do nothing block with infinite loop */
            } while( true );
          }
          *(uint *)((int)piVar6 + uVar7 + 4) = piVar6[1] - uVar7;
          piVar6[1] = uVar7;
          FUN_0800afcc();
        }
        uVar5 = piVar6[1];
        uVar7 = piVar1[1] - uVar5;
        piVar1[1] = uVar7;
        if (uVar7 < (uint)piVar1[2]) {
          piVar1[2] = uVar7;
        }
        piVar6[1] = uVar5 | piVar1[5];
        *piVar6 = 0;
        piVar1[3] = piVar1[3] + 1;
      }
    }
  }
  FUN_0800cc0c();
  if ((uVar8 & 7) == 0) {
    return uVar8;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

