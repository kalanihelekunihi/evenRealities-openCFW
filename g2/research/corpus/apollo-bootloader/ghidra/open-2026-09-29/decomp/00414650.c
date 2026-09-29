
int FUN_00414650(int param_1)

{
  uint uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  bool bVar9;
  int *piVar10;
  uint local_68;
  int local_64;
  int local_60;
  uint local_5c;
  uint local_58;
  uint local_54;
  int local_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined1 auStack_2c [8];
  undefined1 auStack_24 [16];
  
  iVar4 = FUN_00413ff8(param_1);
  if (iVar4 == 0) {
    FUN_004156ac(&local_44,DAT_00415100,0x20);
    FUN_004156ac(auStack_24,DAT_00415104,0x10);
    do {
      iVar4 = FUN_00410ad8(auStack_2c);
      if (iVar4 != 0) {
        iVar4 = FUN_00410bfa(param_1 + 0x30);
        if (iVar4 == 0) {
          FUN_00415fae(DAT_00415268,DAT_004150fc,0x1213,*(undefined4 *)(param_1 + 0x30),
                       *(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),&DAT_00414950
                      );
        }
        iVar4 = lfs_tag_isvalid(*(undefined4 *)(param_1 + 0x30));
        *(uint *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + (uint)(iVar4 == 0);
        *(undefined4 *)(param_1 + 0x3c) = *(undefined4 *)(param_1 + 0x30);
        *(undefined4 *)(param_1 + 0x40) = *(undefined4 *)(param_1 + 0x34);
        *(undefined4 *)(param_1 + 0x44) = *(undefined4 *)(param_1 + 0x38);
        *(uint *)(param_1 + 0x54) =
             *(uint *)(param_1 + 0x2c) -
             *(uint *)(param_1 + 0x6c) * (*(uint *)(param_1 + 0x2c) / *(uint *)(param_1 + 0x6c));
        lfs_alloc_drop(param_1);
        return 0;
      }
      iVar4 = FUN_004145fc(&local_44,auStack_24);
      uVar7 = DAT_00414b44;
      if (iVar4 < 0) break;
      uStack_4c = *(undefined4 *)(DAT_00415110 + 4);
      uStack_48 = *(undefined4 *)(DAT_00415110 + 8);
      piVar10 = &local_50;
      uVar6 = DAT_00415114;
      local_50 = param_1;
      iVar4 = FUN_00411670(param_1,&local_44,auStack_2c,DAT_00414b44,DAT_00415118,0,DAT_00415114,
                           piVar10);
      if (iVar4 < 0) break;
      if ((iVar4 != 0) && (iVar4 = FUN_00410b7c(iVar4), iVar4 == 0)) {
        *(undefined4 *)(param_1 + 0x20) = local_44;
        *(undefined4 *)(param_1 + 0x24) = local_40;
        iVar4 = FUN_004110d0(param_1,&local_44,uVar7,DAT_0041511c,&local_68);
        if (iVar4 < 0) break;
        FUN_00410d1e(&local_68);
        uVar1 = local_68;
        uVar8 = local_68 >> 0x10;
        uVar5 = lfs_fs_disk_version_major(param_1);
        if ((uVar1 >> 0x10 != uVar5) ||
           (uVar5 = lfs_fs_disk_version_minor(param_1), uVar5 < (uVar1 & 0xffff))) {
          uVar2 = lfs_fs_disk_version_minor(param_1);
          uVar3 = lfs_fs_disk_version_major(param_1);
          FUN_00415fae(DAT_0041517c,DAT_004150fc,0x11b9,uVar8,uVar1 & 0xffff,uVar3,uVar2,
                       &DAT_00414950);
          iVar4 = -0x16;
          break;
        }
        uVar5 = lfs_fs_disk_version_minor(param_1);
        bVar9 = (uVar1 & 0xffff) < uVar5;
        if (bVar9) {
          uVar6 = lfs_fs_disk_version_minor(param_1);
          uVar2 = lfs_fs_disk_version_major(param_1);
          piVar10 = (int *)&DAT_00414950;
          uVar6 = uVar6 & 0xffff;
          FUN_00415fae(DAT_00415124,DAT_004150fc,0x11c8,uVar8,uVar1 & 0xffff,uVar2,uVar6,
                       &DAT_00414950);
        }
        FUN_00414c34(param_1,bVar9);
        if (local_5c != 0) {
          if (*(uint *)(param_1 + 0x70) < local_5c) {
            FUN_00415fae(DAT_004151b0,DAT_004150fc,0x11d3,local_5c,*(undefined4 *)(param_1 + 0x70),
                         &DAT_00414950,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x70) = local_5c;
        }
        if (local_58 != 0) {
          if (*(uint *)(param_1 + 0x74) < local_58) {
            FUN_00415fae(DAT_004151b4,DAT_004150fc,0x11de,local_58,*(undefined4 *)(param_1 + 0x74),
                         &DAT_00414950,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x74) = local_58;
        }
        if (local_54 != 0) {
          if (*(uint *)(param_1 + 0x78) < local_54) {
            FUN_00415fae(DAT_004151b8,DAT_004150fc,0x11e9,local_54,*(undefined4 *)(param_1 + 0x78),
                         &DAT_00414950,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x78) = local_54;
          uVar7 = lfs_min(*(undefined4 *)(param_1 + 0x7c),*(undefined4 *)(param_1 + 0x78));
          *(undefined4 *)(param_1 + 0x7c) = uVar7;
        }
        if ((*(int *)(*(int *)(param_1 + 0x68) + 0x20) != 0) &&
           (local_60 != *(int *)(*(int *)(param_1 + 0x68) + 0x20))) {
          FUN_00415fae(DAT_004151bc,DAT_004150fc,0x11f8,local_60,
                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x20),&DAT_00414950,uVar6,piVar10)
          ;
          iVar4 = -0x16;
          break;
        }
        *(int *)(param_1 + 0x6c) = local_60;
        if (local_64 != *(int *)(*(int *)(param_1 + 0x68) + 0x1c)) {
          FUN_00415fae(DAT_004151f8,DAT_004150fc,0x1201,local_64,
                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),&DAT_00414950,uVar6,piVar10)
          ;
          iVar4 = -0x16;
          break;
        }
      }
      iVar4 = FUN_00411c04(param_1,&local_44,param_1 + 0x30);
    } while (iVar4 == 0);
    FUN_00414948(param_1);
  }
  return iVar4;
}

