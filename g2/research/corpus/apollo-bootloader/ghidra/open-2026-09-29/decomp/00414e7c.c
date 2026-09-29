
int FUN_00414e7c(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

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
  iVar5 = FUN_00410c14(param_1 + 0x30);
  if (iVar5 == 0) {
    iVar5 = 0;
  }
  else {
    iVar5 = 0;
    while (iVar5 < 2) {
      FUN_004156ac(&local_a0,DAT_004152f0,0x20);
      bVar1 = false;
LAB_00414eba:
      iVar6 = FUN_00410ad8(&local_88);
      if (iVar6 == 0) {
        iVar6 = FUN_00411be4(param_1,auStack_68,&local_88);
        if (iVar6 != 0) {
          return iVar6;
        }
        if (local_89 != '\0') {
LAB_00415070:
          FUN_004156ac(&local_a0,auStack_68,0x20);
          goto LAB_00414eba;
        }
        iVar6 = FUN_00414baa(param_1,&local_88,auStack_48);
        if ((iVar6 < 0) && (iVar6 != -2)) {
          return iVar6;
        }
        if ((iVar5 == 0) && (iVar6 != -2)) {
          iVar7 = FUN_004110d0(param_1,auStack_48,DAT_00415120,iVar6,&local_a8);
          if (iVar7 < 0) {
            return iVar7;
          }
          FUN_00410b46(&local_a8);
          iVar7 = FUN_00410b1c(&local_a8,&local_88);
          uVar2 = DAT_004150fc;
          if (iVar7 == 0) {
            puVar8 = &DAT_00415014;
            FUN_00415fae(DAT_004152f4,DAT_004150fc,0x13ae,local_88,local_84,local_a8,local_a4,
                         &DAT_00415014);
            uVar4 = 0x3ff;
            iVar6 = FUN_00410c64(param_1 + 0x30,&local_a0);
            if (iVar6 != 0) {
              uVar4 = lfs_tag_id(*(undefined4 *)(param_1 + 0x30));
              FUN_00415fae(DAT_004152f8,uVar2,0x13b8,local_a0,local_9c,uVar4,&DAT_00415014,puVar8);
              FUN_00414cbc(param_1,0x3ff,0);
            }
            FUN_00410b5c(&local_a8);
            FUN_004156ac(local_78,DAT_004152fc,0x10);
            if (uVar4 == 0x3ff) {
              local_78[0] = 0;
            }
            else {
              local_78[0] = DAT_004152dc | (uint)uVar4 << 10;
            }
            local_6c = &local_a8;
            iVar6 = FUN_00412b80(param_1,&local_a0,local_78,2);
            FUN_00410b46(&local_a8);
            if (iVar6 < 0) {
              return iVar6;
            }
            if (iVar6 == 3) {
              bVar1 = true;
            }
            goto LAB_00414eba;
          }
        }
        if (((iVar5 != 1) || (iVar6 != -2)) || (param_2 == '\0')) goto LAB_00415070;
        FUN_00415fae(DAT_00415300,DAT_004150fc,0x13d7,local_88,local_84,&DAT_00415014);
        iVar6 = FUN_00411c04(param_1,auStack_68,param_1 + 0x48);
        if (iVar6 != 0) {
          return iVar6;
        }
        FUN_00410b5c(auStack_50);
        local_80 = DAT_00415304 | (local_51 + 0x600) * 0x100000;
        local_7c = auStack_50;
        iVar6 = FUN_00412b80(param_1,&local_a0,&local_80,1);
        FUN_00410b46(auStack_50);
        if (iVar6 < 0) {
          return iVar6;
        }
        if (iVar6 == 3) {
          bVar1 = true;
        }
        goto LAB_00414eba;
      }
      if (bVar1) {
        iVar5 = 0;
      }
      else {
        iVar5 = iVar5 + 1;
      }
    }
    cVar3 = FUN_00410c2a(param_1 + 0x30);
    iVar5 = FUN_00414c40(param_1,(int)-cVar3);
  }
  return iVar5;
}

