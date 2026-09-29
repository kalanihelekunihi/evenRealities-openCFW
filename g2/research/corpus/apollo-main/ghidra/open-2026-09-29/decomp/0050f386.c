
void FUN_0050f386(int param_1,char param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int local_80;
  undefined1 *local_7c;
  undefined4 local_70;
  undefined4 local_60;
  int local_50;
  
  iVar2 = FUN_0050f710(param_1);
  if (iVar2 != 0) {
    uVar3 = FUN_004997f8(iVar2);
    bVar1 = FUN_0044c448(iVar2,0,uVar3);
    iVar7 = 0;
    if (bVar1 == 1) {
      iVar7 = 0;
    }
    else if (bVar1 != 0) {
      if (bVar1 == 3) {
        iVar7 = FUN_0043fe16(param_1);
        iVar4 = FUN_0043fd9e(iVar2);
        iVar7 = iVar7 - iVar4;
      }
      else if (bVar1 < 3) {
        iVar7 = FUN_0043fe16(param_1);
        iVar4 = FUN_0043fd9e(iVar2);
        iVar7 = (iVar7 - iVar4) / 2;
      }
    }
    FUN_0043f0e0(iVar2,iVar7);
    iVar7 = FUN_0050e9cc(param_1,0);
    iVar4 = FUN_0050e9e0(param_1,0);
    iVar7 = *(int *)(iVar7 + 0xc);
    iVar5 = FUN_0043fe70(param_1);
    iVar6 = FUN_0050e9ea(param_1,0);
    if ((param_2 == '\0') || (iVar6 == 0)) {
      FUN_0050f678(param_1);
    }
    iVar7 = (iVar5 / 2 - iVar7 / 2) - (iVar4 + iVar7) * *(int *)(param_1 + 0x30);
    if ((param_2 == '\0') || (iVar6 == 0)) {
      FUN_00450500(iVar2,&LAB_0050f780_1);
      FUN_0043f142(iVar2,iVar7);
    }
    else {
      FUN_004503d6(&local_80);
      local_7c = &LAB_0050f780_1;
      local_80 = iVar2;
      uVar3 = FUN_0043fce0(iVar2);
      FUN_004506ce(&local_80,uVar3,iVar7);
      local_70 = 0x50f771;
      local_60 = DAT_0050f670;
      local_50 = iVar6;
      FUN_00450408(&local_80);
    }
  }
  return;
}

