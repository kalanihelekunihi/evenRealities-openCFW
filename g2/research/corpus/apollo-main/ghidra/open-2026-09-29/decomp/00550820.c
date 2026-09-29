
undefined8 FUN_00550820(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  uint *puVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar4 = DAT_00550ff4;
  pbVar1 = DAT_00550d38;
  iVar6 = param_1;
  if (*(int *)(DAT_00550ff4 + 0x3c) != 0) {
    if (*DAT_00550d38 == 0) {
      FUN_0044e498(*(undefined4 *)(DAT_00550ff4 + 0x3c));
      iVar5 = service_ancc_message_count_get();
      puVar2 = DAT_00550f7c;
      if (iVar5 == 0) {
        *pbVar1 = 0;
      }
      else if ((param_1 == 1) && ((int)*DAT_00550f7c < iVar5 + -1)) {
        *DAT_00550f7c = *DAT_00550f7c + 1;
        sVar3 = FUN_00550170(*puVar2 & 0xff);
        if (-1 < sVar3) {
          *pbVar1 = 1;
          FUN_00550694(*(undefined4 *)(iVar4 + 0x3c),sVar3 * 0xd6,*DAT_005514d4);
        }
        FUN_00550e2e(*puVar2,1);
      }
      else if ((param_1 == -1) && (0 < (int)*DAT_00550f7c)) {
        *DAT_00550f7c = *DAT_00550f7c - 1;
        sVar3 = FUN_00550170(*puVar2 & 0xff);
        if (-1 < sVar3) {
          *pbVar1 = 1;
          FUN_00550694(*(undefined4 *)(iVar4 + 0x3c),sVar3 * 0xd6,*DAT_005514d4);
        }
        FUN_00550e2e(*puVar2,1);
      }
      else {
        FUN_00550708(param_1);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      iVar6 = param_1;
      if (iVar4 << 0x1e < 0) {
        param_3 = (uint)*pbVar1;
        iVar6 = 0x355;
        param_2 = DAT_00551310;
        FUN_0043d574(3,DAT_00550958,DAT_00550954,DAT_00551314,0x355,DAT_00551310,param_3,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00551318,DAT_00551318,*pbVar1,iVar6,param_2,param_3);
      }
    }
  }
  return CONCAT44(param_2,iVar6);
}

