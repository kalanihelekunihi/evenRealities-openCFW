
int * FUN_0048925a(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  char cVar3;
  byte bVar4;
  char cVar5;
  int *piVar6;
  int iVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  undefined4 local_58;
  uint local_54;
  undefined4 local_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  int *local_44;
  int local_40;
  char local_3c;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  FUN_00488f40(param_2,0xc);
  iVar11 = *(int *)(param_1 + 0xc);
  cVar1 = *(char *)(param_1 + 0x10);
  if ((cVar1 == '\0') && (*(int *)(iVar11 + 0x10) == 0)) {
    piVar6 = (int *)0x0;
  }
  else {
    cVar3 = FUN_004d4c2c();
    iVar2 = DAT_00489420;
    if ((cVar3 == '\0') ||
       ((cVar1 != '\x01' ||
        (local_40 = iVar11, local_3c = cVar1,
        iVar7 = FUN_004d4dca(*(undefined4 *)(DAT_00489420 + 0x138),&local_40,0), iVar7 == 0)))) {
      if ((cVar1 == '\x01') && (bVar4 = FUN_004c6d9a(param_1 + 0x14,iVar11,2), bVar4 != 0)) {
        local_54 = (uint)bVar4;
        local_58 = DAT_00489454;
        FUN_0044d25c(3,DAT_00489434,0x150,DAT_00489458);
        piVar6 = (int *)0x0;
      }
      else {
        iVar2 = DAT_00489420;
        iVar7 = DAT_00489420 + 0x128;
        for (piVar6 = (int *)FUN_00482cd8(iVar7); piVar6 != (int *)0x0;
            piVar6 = (int *)FUN_00482cf0(iVar7,piVar6)) {
          if ((*piVar6 != 0) && (piVar6[1] != 0)) {
            FUN_004c6fba(param_1 + 0x14,0,0);
            cVar5 = (*(code *)*piVar6)(piVar6,param_1,param_2);
            if (cVar5 == '\x01') {
              if ((param_2[2] & 0xffff) == 0) {
                uVar8 = FUN_004893e6(param_2);
                param_2[2] = param_2[2] & 0xffff0000 | uVar8 & 0xffff;
              }
              break;
            }
          }
        }
        if (cVar1 == '\x01') {
          FUN_004c6ee0(param_1 + 0x14);
        }
        if (((cVar3 != '\0') && (cVar1 == '\x01')) && (piVar6 != (int *)0x0)) {
          local_54 = CONCAT31(local_54._1_3_,1);
          local_58 = FUN_004547c6(iVar11);
          local_50 = *param_2;
          uStack_4c = param_2[1];
          uStack_48 = param_2[2];
          local_44 = piVar6;
          iVar11 = FUN_004d4eea(*(undefined4 *)(iVar2 + 0x138),&local_58,0);
          if (iVar11 == 0) {
            FUN_0044f758(local_58);
            piVar6 = (int *)0x0;
          }
          else {
            FUN_004d4e72(*(undefined4 *)(iVar2 + 0x138),iVar11,0);
          }
        }
      }
    }
    else {
      iVar11 = FUN_004d5396(iVar7);
      uVar9 = *(undefined4 *)(iVar11 + 0xc);
      uVar10 = *(undefined4 *)(iVar11 + 0x10);
      *param_2 = *(undefined4 *)(iVar11 + 8);
      param_2[1] = uVar9;
      param_2[2] = uVar10;
      piVar6 = *(int **)(iVar11 + 0x14);
      FUN_004d4e72(*(undefined4 *)(iVar2 + 0x138),iVar7,0);
    }
  }
  return piVar6;
}

