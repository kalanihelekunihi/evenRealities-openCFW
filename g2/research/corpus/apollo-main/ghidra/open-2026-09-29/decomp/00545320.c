
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00545320(undefined4 *param_1,int param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    FUN_004733ee(DAT_00545534);
    uVar1 = FUN_00585c94(0);
    FUN_004733ee(DAT_00545538,_MasterStackPointer,uVar1);
    FUN_004733ee(DAT_00545570,&DAT_0054552c,DAT_0054556c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 == 0) {
    if (*(char *)(param_1 + 6) != '\0') {
      FUN_004733ee(DAT_00545534);
      uVar1 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00545538,*param_1,uVar1);
      FUN_004733ee(DAT_00545570,DAT_00545574,DAT_0054556c);
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    param_1[3] = *param_3;
  }
  else if (param_2 == 1) {
    *param_3 = param_1[3];
  }
  else if (param_2 == 2) {
    param_1[7] = param_3;
  }
  else if (param_2 == 3) {
    param_1[8] = param_3;
  }
  else if (param_2 == 9) {
    FUN_004733ee(DAT_00545534);
    uVar1 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00545538,*param_1,uVar1);
    FUN_004733ee(DAT_00545578);
  }
  else if ((param_2 != 10) && (param_2 == 0xb)) {
    if (*(char *)(param_1 + 6) != '\0') {
      FUN_004733ee(DAT_00545534);
      uVar1 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00545538,*param_1,uVar1);
      FUN_004733ee(DAT_00545570,DAT_00545574,DAT_0054556c);
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    *(undefined1 *)((int)param_1 + 0x1a) = *(undefined1 *)param_3;
  }
  return;
}

