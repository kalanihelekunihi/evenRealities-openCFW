
/* WARNING: Restarted to delay deadcode elimination for space: register */

int gx8002_flash_probe(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  longlong lVar1;
  byte *pbVar2;
  uint *puVar3;
  uint uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined4 uVar9;
  
  uVar8 = param_2;
  uVar5 = gx8002_clock_time_us();
  uVar4 = uRam100247b4;
  puVar3 = puRam100247b0;
  pbVar2 = pbRam100247ac;
  uVar9 = uVar8;
  do {
    if ((*pbVar2 < 2) &&
       (uVar9 = param_2, iVar6 = (*(code *)(*puVar3 & 0xfffffffe))(param_1,param_2,param_3,param_4),
       iVar6 != 0)) {
      *pbVar2 = 1;
      return iVar6;
    }
    uVar7 = gx8002_clock_time_us();
    lVar1 = CONCAT44(uVar9,uVar7) - CONCAT44(uVar8,uVar5);
  } while (((int)((ulonglong)lVar1 >> 0x20) == 0) && (uVar9 = 0, (uint)lVar1 <= uVar4));
  return 0;
}

