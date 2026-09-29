
undefined4 FUN_0048fe98(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  short sVar6;
  short sVar7;
  int iVar8;
  undefined1 local_68;
  char local_67;
  short local_66;
  uint local_64;
  uint local_60;
  uint local_5c [4];
  short local_4c;
  ushort local_48;
  ushort local_44;
  short local_40;
  byte local_3e;
  int *local_38;
  short *local_34;
  undefined4 local_2c;
  undefined4 local_28;
  
  uVar4 = 0;
  iVar5 = 0;
  sVar6 = -1;
  local_66 = 0;
  sVar7 = 0;
  local_2c = param_2;
  local_28 = param_3;
  FUN_0043c0e4(local_5c,8,0);
  local_60 = 0xffffffff;
  iVar1 = FUN_004d9384(local_5c + 2,local_2c,local_28);
  if (((iVar1 == 0) || (param_4 << 0x1f < 0)) || (iVar1 = FUN_0048fdf2(local_5c + 2), iVar1 != 0)) {
LAB_0048ff58:
    do {
      if (*(int *)(param_1 + 8) == 0) {
LAB_0048ff78:
        if ((sVar6 != -1) && (local_66 != sVar7)) {
          uVar2 = DAT_004905bc;
          if (*(int *)(param_1 + 0xc) != 0) {
            uVar2 = *(undefined4 *)(param_1 + 0xc);
          }
          *(undefined4 *)(param_1 + 0xc) = uVar2;
          return 0;
        }
        uVar3 = *(ushort *)(local_5c[2] + 0x12);
        uVar4 = (uint)uVar3;
        if (uVar3 != 0) {
          if (0x40 < uVar3) {
            uVar4 = 0x40;
          }
          for (uVar3 = 0; (uint)uVar3 < uVar4 >> 5; uVar3 = uVar3 + 1) {
            if (local_5c[uVar3] != local_60) {
              uVar2 = DAT_004905c0;
              if (*(int *)(param_1 + 0xc) != 0) {
                uVar2 = *(undefined4 *)(param_1 + 0xc);
              }
              *(undefined4 *)(param_1 + 0xc) = uVar2;
              return 0;
            }
          }
          if (((uVar4 & 0x1f) != 0) &&
             (local_5c[(int)uVar4 >> 5] != local_60 >> (0x20 - (uVar4 & 0x1f) & 0xff))) {
            uVar2 = DAT_004905c0;
            if (*(int *)(param_1 + 0xc) != 0) {
              uVar2 = *(undefined4 *)(param_1 + 0xc);
            }
            *(undefined4 *)(param_1 + 0xc) = uVar2;
            return 0;
          }
        }
        return 1;
      }
      iVar1 = FUN_0048f66c(param_1,&local_68,&local_64,&local_67);
      if (iVar1 == 0) {
        if (local_67 == '\0') {
          return 0;
        }
        goto LAB_0048ff78;
      }
      if (local_64 == 0) {
        if (-1 < param_4 << 0x1d) {
          uVar2 = DAT_004905b8;
          if (*(int *)(param_1 + 0xc) != 0) {
            uVar2 = *(undefined4 *)(param_1 + 0xc);
          }
          *(undefined4 *)(param_1 + 0xc) = uVar2;
          return 0;
        }
        goto LAB_0048ff78;
      }
      iVar1 = FUN_004d93f8(local_5c + 2,local_64);
      if ((iVar1 != 0) && ((local_3e & 0xf) != 10)) {
        if (((local_3e & 0x30) == 0x20) && (local_34 == &local_40)) {
          if (sVar6 != local_4c) {
            if ((sVar6 != -1) && (local_66 != sVar7)) {
              uVar2 = DAT_004905bc;
              if (*(int *)(param_1 + 0xc) != 0) {
                uVar2 = *(undefined4 *)(param_1 + 0xc);
              }
              *(undefined4 *)(param_1 + 0xc) = uVar2;
              return 0;
            }
            local_66 = 0;
            sVar7 = local_40;
            sVar6 = local_4c;
          }
          local_34 = &local_66;
        }
        if (((local_3e & 0x30) == 0) && (local_48 < 0x40)) {
          local_5c[(int)(uint)local_48 >> 5] =
               1 << ((byte)local_48 & 0x1f) | local_5c[(int)(uint)local_48 >> 5];
        }
        iVar1 = FUN_0048fbe4(param_1,local_68,local_5c + 2);
        if (iVar1 == 0) {
          return 0;
        }
        goto LAB_0048ff58;
      }
      if (uVar4 == 0) {
        iVar1 = FUN_004d946e(local_5c + 2);
        if (iVar1 != 0) {
          iVar5 = *local_38;
          uVar4 = (uint)local_44;
        }
        if (iVar5 == 0) {
          uVar4 = 0xffffffff;
        }
      }
      if (uVar4 <= local_64) {
        iVar8 = *(int *)(param_1 + 8);
        iVar1 = FUN_0048fc88(param_1,local_64,local_68,iVar5);
        if (iVar1 == 0) {
          return 0;
        }
        if (iVar8 != *(int *)(param_1 + 8)) goto LAB_0048ff58;
      }
      iVar1 = FUN_0048f6a0(param_1,local_68);
    } while (iVar1 != 0);
  }
  else {
    uVar2 = DAT_004905a8;
    if (*(int *)(param_1 + 0xc) != 0) {
      uVar2 = *(undefined4 *)(param_1 + 0xc);
    }
    *(undefined4 *)(param_1 + 0xc) = uVar2;
  }
  return 0;
}

