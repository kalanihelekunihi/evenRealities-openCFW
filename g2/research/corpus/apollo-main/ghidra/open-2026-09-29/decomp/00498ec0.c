
void FUN_00498ec0(int *param_1)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int local_11c;
  int local_118;
  int local_114;
  int local_110;
  undefined1 auStack_10c [8];
  undefined1 auStack_104 [16];
  undefined1 auStack_f4 [16];
  undefined1 auStack_e4 [16];
  int local_d4;
  undefined4 local_c8;
  undefined4 local_b8;
  undefined4 local_b4;
  undefined4 local_b0;
  undefined4 local_ac;
  undefined1 auStack_a0 [12];
  undefined2 local_94;
  int local_8c;
  int local_88;
  undefined4 local_7c;
  undefined1 auStack_78 [16];
  int local_68;
  undefined4 local_5c;
  
  iVar1 = FUN_00450286(param_1);
  iVar2 = *param_1;
  if (iVar1 == 0x1a) {
    pcVar3 = (char *)param_1[4];
    if (*pcVar3 != '\x02') {
      if (((*(byte *)(iVar2 + 0x58) & 3) == 3) || ((*(byte *)(iVar2 + 0x58) & 3) == 2)) {
        *pcVar3 = '\x01';
      }
      else {
        iVar1 = FUN_00440fc4((*(uint *)(iVar2 + 0x58) & 0x7f) >> 2);
        if (iVar1 == 0) {
          iVar1 = FUN_00498634(iVar2,0);
          if (iVar1 == 0xff) {
            if (*(int *)(iVar2 + 0x44) == 0) {
              if ((*(int *)(iVar2 + 0x48) == 0x100) && (*(int *)(iVar2 + 0x4c) == 0x100)) {
                iVar1 = FUN_00450f28(*(undefined4 *)(pcVar3 + 4),iVar2 + 0x14,0);
                if (iVar1 == 0) {
                  *pcVar3 = '\x01';
                  return;
                }
              }
              else {
                FUN_00498b82(iVar2,auStack_10c);
                uVar4 = FUN_0043fdda(iVar2);
                uVar5 = FUN_0043fd9e(iVar2);
                FUN_00488cda(&local_11c,uVar5,uVar4,0,*(uint *)(iVar2 + 0x48) & 0xffff,
                             *(uint *)(iVar2 + 0x4c) & 0xffff,auStack_10c);
                local_11c = *(int *)(iVar2 + 0x14) + local_11c;
                local_118 = *(int *)(iVar2 + 0x18) + local_118;
                local_114 = *(int *)(iVar2 + 0x14) + local_114;
                local_110 = *(int *)(iVar2 + 0x18) + local_110;
                iVar1 = FUN_00450f28(*(undefined4 *)(pcVar3 + 4),&local_11c,0);
                if (iVar1 == 0) {
                  *pcVar3 = '\x01';
                  return;
                }
              }
              if (*(int *)(iVar2 + 0x30) != 0) {
                *pcVar3 = '\x01';
              }
            }
            else {
              *pcVar3 = '\x01';
            }
          }
          else {
            *pcVar3 = '\x01';
          }
        }
        else {
          *pcVar3 = '\x01';
        }
      }
    }
  }
  else if ((((iVar1 == 0x1d) && (*(int *)(iVar2 + 0x40) != 0)) && (*(int *)(iVar2 + 0x3c) != 0)) &&
          ((*(int *)(iVar2 + 0x48) != 0 && (*(int *)(iVar2 + 0x4c) != 0)))) {
    iVar1 = FUN_00451960(param_1);
    if (((*(byte *)(iVar2 + 0x58) & 3) == 1) || ((*(byte *)(iVar2 + 0x58) & 3) == 0)) {
      FUN_00488918(auStack_e4);
      local_d4 = iVar1;
      FUN_00452a34(iVar2,0,auStack_e4);
      FUN_00439c04(auStack_f4,iVar1 + 0x18,0x10);
      FUN_00498b82(iVar2,auStack_a0);
      local_b0 = *(undefined4 *)(iVar2 + 0x48);
      local_ac = *(undefined4 *)(iVar2 + 0x4c);
      local_b4 = *(undefined4 *)(iVar2 + 0x44);
      local_94 = local_94 & 0xf7ff;
      local_94 = CONCAT11((byte)(*(uint *)(iVar2 + 0x58) >> 0xc) & 7 |
                          (byte)(local_94 >> 8) & 0xf8 |
                          (byte)(((*(uint *)(iVar2 + 0x58) >> 7 & 1) << 0xb) >> 8),
                          (undefined1)local_94);
      local_7c = *(undefined4 *)(iVar2 + 0x30);
      local_c8 = *(undefined4 *)(iVar2 + 0x2c);
      FUN_00450b5c(&local_8c,*(undefined4 *)(iVar2 + 0x14),*(undefined4 *)(iVar2 + 0x18),
                   *(int *)(iVar2 + 0x3c) + *(int *)(iVar2 + 0x14) + -1,
                   *(int *)(iVar2 + 0x40) + *(int *)(iVar2 + 0x18) + -1);
      local_b8 = FUN_0049865e(iVar2,0);
      if ((*(uint *)(iVar2 + 0x58) & 0xfff) >> 8 < 10) {
        FUN_00451082(iVar2 + 0x14,&local_8c,*(uint *)(iVar2 + 0x58) >> 8 & 0xf,
                     *(undefined4 *)(iVar2 + 0x34),*(undefined4 *)(iVar2 + 0x38));
        FUN_00439c04(auStack_104,&local_8c,0x10);
      }
      else if ((*(uint *)(iVar2 + 0x58) & 0xfff) >> 8 == 0xc) {
        FUN_00450bcc(iVar1 + 0x18,iVar1 + 0x18,iVar2 + 0x14);
        FUN_00450bb2(&local_8c,*(undefined4 *)(iVar2 + 0x34),*(undefined4 *)(iVar2 + 0x38));
        FUN_00450bb2(&local_8c,
                     *(int *)(iVar2 + 0x3c) *
                     ((((*(int *)(iVar1 + 0x18) - local_8c) - *(int *)(iVar2 + 0x3c)) + 1) /
                     *(int *)(iVar2 + 0x3c)),
                     *(int *)(iVar2 + 0x40) *
                     ((((*(int *)(iVar1 + 0x1c) - local_88) - *(int *)(iVar2 + 0x40)) + 1) /
                     *(int *)(iVar2 + 0x40)));
        FUN_00439c04(auStack_104,iVar1 + 0x18,0x10);
        local_94 = local_94 | 0x1000;
      }
      else {
        FUN_00439c04(auStack_104,&local_8c,0x10);
      }
      FUN_00488a38(iVar1,auStack_e4,auStack_104);
      FUN_00439c04(iVar1 + 0x18,auStack_f4,0x10);
    }
    else if ((*(byte *)(iVar2 + 0x58) & 3) == 2) {
      FUN_00489f5e(auStack_78);
      local_68 = iVar1;
      FUN_00452988(iVar2,0,auStack_78);
      local_5c = *(undefined4 *)(iVar2 + 0x2c);
      FUN_00489fe0(iVar1,auStack_78,iVar2 + 0x14);
    }
    else if (*(int *)(iVar2 + 0x2c) == 0) {
      FUN_0044d25c(2,DAT_004991d8,0x339,DAT_004991d4,DAT_004991d0);
    }
    else {
      FUN_0044d25c(2,DAT_004991d8,0x33d,DAT_004991d4,DAT_004991dc);
    }
  }
  return;
}

