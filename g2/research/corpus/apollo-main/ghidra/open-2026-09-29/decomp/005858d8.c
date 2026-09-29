
undefined8
FUN_005858d8(undefined4 param_1,int param_2,uint param_3,uint param_4,uint param_5,byte param_6)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint local_18;
  
  if (param_4 <= param_5) {
    FUN_004733ee(DAT_00585988);
    FUN_004733ee(&DAT_00585980);
    FUN_004733ee(DAT_00585994,DAT_00585990,DAT_0058598c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_3 == 0) {
    FUN_004733ee(DAT_00585988);
    FUN_004733ee(&DAT_00585980);
    FUN_004733ee(DAT_00585994,DAT_00585998,DAT_0058598c);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iVar2 = FUN_00585870(param_3,param_4);
  if (iVar2 == -1) {
    uVar3 = 0;
    local_18 = param_3;
  }
  else {
    local_18 = (uint)param_6;
    bVar1 = FUN_00585a52(param_1,iVar2 + param_2,param_3 + iVar2,1);
    uVar3 = (uint)bVar1;
  }
  return CONCAT44(local_18,uVar3);
}

