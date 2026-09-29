
undefined8 FUN_00585a74(int *param_1,int param_2,int param_3,undefined4 param_4,int param_5)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 == (int *)0x0) {
    FUN_004733ee(DAT_00585c50);
    FUN_004733ee(&DAT_00585c48);
    FUN_004733ee(DAT_00585c58,&DAT_00585c4c,DAT_00585c54);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_2 == 0) {
    FUN_004733ee(DAT_00585c50);
    FUN_004733ee(&DAT_00585c48);
    FUN_004733ee(DAT_00585c58,DAT_00585c5c,DAT_00585c54);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_3 == 0) {
    FUN_004733ee(DAT_00585c50);
    FUN_004733ee(&DAT_00585c48);
    FUN_004733ee(DAT_00585c58,DAT_00585c60,DAT_00585c54);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if ((char)param_1[6] == '\0') {
    *param_1 = param_2;
    *(char *)(param_1 + 1) = (char)param_4;
    param_1[9] = param_5;
    if (*(char *)((int)param_1 + 0x19) == '\0') {
      FUN_00597dec();
      iVar2 = FUN_00597cde(param_3);
      param_1[2] = iVar2;
      if (iVar2 == 0) {
        FUN_004733ee(DAT_00585c50);
        FUN_004733ee(&DAT_00585c48);
        FUN_004733ee(DAT_00585c64,param_3);
        uVar1 = 4;
        goto LAB_00585bc6;
      }
      iVar2 = FUN_00597e54(param_1[2] + 0x1c);
      uVar3 = *(uint *)(iVar2 + 0x20);
      if (param_1[3] == 0) {
        param_1[3] = uVar3;
      }
      else if (param_1[3] != uVar3 * ((uint)param_1[3] / uVar3)) {
        FUN_004733ee(DAT_00585c50);
        FUN_004733ee(&DAT_00585c48);
        FUN_004733ee(DAT_00585c6c,param_1[3],uVar3);
        uVar1 = 8;
        goto LAB_00585bc6;
      }
      param_1[4] = *(int *)(param_1[2] + 0x38);
    }
    if ((param_1[3] & param_1[3] - 1U) != 0) {
      FUN_004733ee(DAT_00585c50);
      FUN_004733ee(&DAT_00585c48);
      FUN_004733ee(DAT_00585c58,DAT_00585c68,DAT_00585c54);
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    if (param_1[4] == param_1[3] * ((uint)param_1[4] / (uint)param_1[3])) {
      if ((uint)param_1[4] / (uint)param_1[3] < 2) {
        FUN_004733ee(DAT_00585c50);
        FUN_004733ee(&DAT_00585c48);
        FUN_004733ee(DAT_00585c74,(uint)param_1[4] / (uint)param_1[3]);
        uVar1 = 8;
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      FUN_004733ee(DAT_00585c50);
      FUN_004733ee(&DAT_00585c48);
      FUN_004733ee(DAT_00585c70,param_1[4],param_1[3]);
      uVar1 = 8;
    }
  }
  else {
    uVar1 = 0;
  }
LAB_00585bc6:
  return CONCAT44(param_4,uVar1);
}

