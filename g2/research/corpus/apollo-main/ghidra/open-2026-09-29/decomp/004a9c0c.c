
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong ui_onboarding_main_sub_004A9C0C
                   (undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int *piVar2;
  char *pcVar3;
  char cVar4;
  ushort uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  uStack_20 = param_2;
  uStack_1c = param_3;
  uStack_18 = param_4;
  FUN_0050fe56();
  pcVar3 = DAT_004a9f68;
  if (*(int *)(DAT_004a9f68 + 4) == 0) {
    uVar6 = osKernelGetTickCount();
    *(undefined4 *)(pcVar3 + 4) = uVar6;
  }
  else {
    cVar4 = FUN_0045a568();
    iVar7 = osKernelGetTickCount();
    piVar2 = DAT_004a9ddc;
    uVar8 = iVar7 - *(int *)(pcVar3 + 4);
    cVar1 = *pcVar3;
    if (cVar1 == '\0') {
      if ((*DAT_004a9ddc != 0) && (uVar5 = FUN_0050ecee(*DAT_004a9ddc), uVar5 != 0)) {
        uVar8 = uVar8 / 6000 - (uint)uVar5 * ((uVar8 / 6000) / (uint)uVar5);
        uVar5 = func_0x0050ec94(*piVar2);
        if (((uVar8 & 0xffff) != (uint)uVar5) && (cVar4 == '\x01')) {
          uStack_1c = CONCAT22(*(undefined2 *)PTR_DAT_004aa22c,(undefined2)uStack_1c);
          uStack_1c = CONCAT13((char)uVar8,(undefined3)uStack_1c);
          FUN_00464bb2(0x10,(int)&uStack_1c + 2,2,0);
        }
      }
    }
    else if (cVar1 == '\x02') {
      cVar1 = pcVar3[1];
      if ((((cVar1 == '\x01') || (cVar1 == '\x03')) || (cVar1 == '\x05')) ||
         (((cVar1 == '\a' || (cVar1 == '\t')) || (cVar1 == '\f')))) {
        if ((0x5db < uVar8) && (cVar4 == '\x01')) {
          uStack_1c._0_2_ = CONCAT11(cVar1,(char)*(undefined2 *)PTR_DAT_004aa230);
          FUN_00464bb2(0x10,&uStack_1c,2,0);
        }
      }
      else if (((cVar1 == '\n') && (0x9c3 < uVar8)) && (cVar4 == '\x01')) {
        uStack_20 = CONCAT22(*(undefined2 *)PTR_DAT_004aa234,(undefined2)uStack_20);
        uStack_20 = CONCAT13(10,(undefined3)uStack_20);
        FUN_00464bb2(0x10,(int)&uStack_20 + 2,2,0);
      }
    }
    else if (((cVar1 == '\x03') && (*DAT_004aa20c == '\x01')) &&
            ((2999 < uVar8 && (*DAT_004aa20c = '\0', cVar4 == '\x01')))) {
      uStack_20 = CONCAT31(uStack_20._1_3_,*_DAT_004aab48);
      FUN_00464bb2(0x10,&uStack_20,1,0);
    }
  }
  return (ulonglong)uStack_20 << 0x20;
}

