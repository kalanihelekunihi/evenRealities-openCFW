
/* WARNING: Restarted to delay deadcode elimination for space: register */

int FUN_100033ac(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  longlong lVar1;
  byte *pbVar2;
  uint *puVar3;
  uint uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  
  uVar8 = param_2;
  uVar5 = FUN_10004da4();
  uVar4 = DAT_10003410;
  puVar3 = DAT_1000340c;
  pbVar2 = DAT_10003408;
  uVar9 = uVar8;
  do {
    if (*pbVar2 < 2) {
      uVar9 = param_2;
      iVar7 = (*(code *)(*puVar3 & 0xfffffffe))(param_1,param_2,param_3,param_4);
      if (iVar7 != 0) {
        *pbVar2 = 1;
        return iVar7;
      }
    }
    uVar6 = FUN_10004da4();
    lVar1 = CONCAT44(uVar9,uVar6) - CONCAT44(uVar8,uVar5);
  } while (((int)((ulonglong)lVar1 >> 0x20) == 0) && (uVar9 = 0, (uint)lVar1 <= uVar4));
  FUN_100061a4(PTR_s_flash_probe_waitting_timeout__10003414);
  return 0;
}

