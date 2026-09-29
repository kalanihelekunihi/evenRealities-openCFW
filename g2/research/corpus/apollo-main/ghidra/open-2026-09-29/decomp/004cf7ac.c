
int FUN_004cf7ac(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined *puVar8;
  undefined4 local_a8;
  undefined4 local_a4;
  undefined4 local_a0;
  undefined4 local_9c;
  char local_89;
  undefined4 local_88;
  undefined4 local_84;
  uint local_80;
  undefined1 *local_7c;
  uint local_78 [3];
  undefined4 *local_6c;
  undefined1 auStack_68 [23];
  byte local_51;
  undefined1 auStack_50 [8];
  undefined1 auStack_48 [32];
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  iVar5 = FUN_004caf0c(param_1 + 0x30);
  if (iVar5 == 0) {
    iVar5 = 0;
  }
  else {
    iVar5 = 0;
    while (iVar5 < 2) {
      FUN_00439c04(&local_a0,DAT_004cfccc,0x20);
      bVar1 = false;
LAB_004cf7ea:
      iVar6 = FUN_004cadd0(&local_88);
      if (iVar6 == 0) {
        iVar6 = FUN_004cbedc(param_1,auStack_68,&local_88);
        if (iVar6 != 0) {
          return iVar6;
        }
        if (local_89 != '\0') {
LAB_004cf9a0:
          FUN_00439c04(&local_a0,auStack_68,0x20);
          goto LAB_004cf7ea;
        }
        iVar6 = FUN_004cf4da(param_1,&local_88,auStack_48);
        if ((iVar6 < 0) && (iVar6 != -2)) {
          return iVar6;
        }
        if ((iVar5 == 0) && (iVar6 != -2)) {
          iVar7 = FUN_004cb3c8(param_1,auStack_48,DAT_004cfa50,iVar6,&local_a8);
          if (iVar7 < 0) {
            return iVar7;
          }
          FUN_004cae3e(&local_a8);
          iVar7 = FUN_004cae14(&local_a8,&local_88);
          uVar2 = DAT_004cfa2c;
          if (iVar7 == 0) {
            puVar8 = &DAT_004cf944;
            FUN_004733ee(DAT_004cfcd0,DAT_004cfa2c,0x13ae,local_88,local_84,local_a8,local_a4,
                         &DAT_004cf944);
            uVar4 = 0x3ff;
            iVar6 = FUN_004caf5c(param_1 + 0x30,&local_a0);
            if (iVar6 != 0) {
              uVar4 = FUN_004caeb0(*(undefined4 *)(param_1 + 0x30));
              FUN_004733ee(DAT_004cfcd4,uVar2,0x13b8,local_a0,local_9c,uVar4,&DAT_004cf944,puVar8);
              FUN_004cf5ec(param_1,0x3ff,0);
            }
            FUN_004cae54(&local_a8);
            FUN_00439c04(local_78,DAT_004cfcd8,0x10);
            if (uVar4 == 0x3ff) {
              local_78[0] = 0;
            }
            else {
              local_78[0] = DAT_004cfcb8 | (uint)uVar4 << 10;
            }
            local_6c = &local_a8;
            iVar6 = FUN_004ccf7c(param_1,&local_a0,local_78,2);
            FUN_004cae3e(&local_a8);
            if (iVar6 < 0) {
              return iVar6;
            }
            if (iVar6 == 3) {
              bVar1 = true;
            }
            goto LAB_004cf7ea;
          }
        }
        if (((iVar5 != 1) || (iVar6 != -2)) || (param_2 == '\0')) goto LAB_004cf9a0;
        FUN_004733ee(DAT_004cfcdc,DAT_004cfa2c,0x13d7,local_88,local_84,&DAT_004cf944);
        iVar6 = FUN_004cbefc(param_1,auStack_68,param_1 + 0x48);
        if (iVar6 != 0) {
          return iVar6;
        }
        FUN_004cae54(auStack_50);
        local_80 = DAT_004cfce0 | (local_51 + 0x600) * 0x100000;
        local_7c = auStack_50;
        iVar6 = FUN_004ccf7c(param_1,&local_a0,&local_80,1);
        FUN_004cae3e(auStack_50);
        if (iVar6 < 0) {
          return iVar6;
        }
        if (iVar6 == 3) {
          bVar1 = true;
        }
        goto LAB_004cf7ea;
      }
      if (bVar1) {
        iVar5 = 0;
      }
      else {
        iVar5 = iVar5 + 1;
      }
    }
    cVar3 = FUN_004caf22(param_1 + 0x30);
    iVar5 = FUN_004cf570(param_1,(int)-cVar3);
  }
  return iVar5;
}

