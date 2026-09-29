
undefined4 FUN_00593a78(undefined4 param_1,undefined4 *param_2,int *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  uVar3 = DAT_00594498;
  uVar2 = DAT_00594494;
  uVar1 = DAT_00594490;
  uVar4 = DAT_0059448c;
  if (param_2 == (undefined4 *)0x0) {
    FUN_0047da78(DAT_0059448c,DAT_00594490,DAT_00594494);
    FUN_0047da78(&DAT_00593c30);
    FUN_004733ee(uVar4,uVar1,uVar2);
    FUN_004733ee(&DAT_00593c30);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  if (param_3 == (int *)0x0) {
    FUN_0047da78(DAT_0059448c,DAT_00594498,DAT_00594494);
    FUN_0047da78(&DAT_00593c30);
    FUN_004733ee(uVar4,uVar3,uVar2);
    FUN_004733ee(&DAT_00593c30);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  uVar4 = FUN_0045601e();
  *param_2 = uVar4;
  iVar5 = FUN_00456026();
  *param_3 = iVar5 << 2;
  return param_4;
}

