
undefined4 FUN_00593afe(undefined4 *param_1,int param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  
  iVar1 = DAT_00594330;
  iVar4 = 0x10;
  puVar5 = param_3;
  if (*DAT_005944a4 != '\0') {
    if (*DAT_005944a8 == '\0') {
      FUN_0047da78(*(undefined4 *)(DAT_00594330 + 0x1c),param_3);
      FUN_0047da78(&DAT_00593c30);
      FUN_004733ee(*(undefined4 *)(iVar1 + 0x1c),param_3);
      FUN_004733ee(&DAT_00593c30);
    }
    else {
      FUN_0047da78(*(undefined4 *)(DAT_00594330 + 0x18),param_3);
      FUN_0047da78(&DAT_00593c30);
      FUN_004733ee(*(undefined4 *)(iVar1 + 0x18),param_3);
      FUN_004733ee(&DAT_00593c30);
    }
    puVar5 = param_1;
    if ((param_1 <= param_3) && (puVar5 = param_3, (undefined4 *)(param_2 + (int)param_1) < param_3)
       ) {
      puVar5 = (undefined4 *)(param_2 + (int)param_1);
    }
  }
  iVar1 = DAT_00594330;
  FUN_0047da78(*(undefined4 *)(DAT_00594330 + 0x10));
  FUN_0047da78(&DAT_00593c30);
  FUN_004733ee(*(undefined4 *)(iVar1 + 0x10));
  FUN_004733ee(&DAT_00593c30);
  for (; (uVar3 = DAT_005944b0, uVar2 = DAT_005944ac,
         puVar5 < (undefined4 *)(param_2 + (int)param_1) && (iVar4 != 0)); iVar4 = iVar4 + -1) {
    FUN_0047da78(DAT_005944ac,puVar5,*puVar5);
    FUN_0047da78(&DAT_00593c30);
    FUN_004733ee(uVar2,puVar5,*puVar5);
    FUN_004733ee(&DAT_00593c30);
    puVar5 = puVar5 + 1;
  }
  FUN_0047da78(DAT_005944b0);
  FUN_0047da78(&DAT_00593c30);
  FUN_004733ee(uVar3);
  FUN_004733ee(&DAT_00593c30);
  return param_4;
}

