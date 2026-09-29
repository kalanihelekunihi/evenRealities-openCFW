
int FUN_004cef78(int param_1)

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
  
  iVar4 = FUN_004ce914(param_1);
  if (iVar4 == 0) {
    FUN_00439c04(&local_44,DAT_004cfa30,0x20);
    FUN_00439c04(auStack_24,DAT_004cfa34,0x10);
    do {
      iVar4 = FUN_004cadd0(auStack_2c);
      if (iVar4 != 0) {
        iVar4 = FUN_004caef2(param_1 + 0x30);
        if (iVar4 == 0) {
          FUN_004733ee(DAT_004cfc18,DAT_004cfa2c,0x1213,*(undefined4 *)(param_1 + 0x30),
                       *(undefined4 *)(param_1 + 0x34),*(undefined4 *)(param_1 + 0x38),&DAT_004cf27c
                      );
        }
        iVar4 = FUN_004cae6a(*(undefined4 *)(param_1 + 0x30));
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
      iVar4 = FUN_004cef18(&local_44,auStack_24);
      uVar7 = DAT_004cf474;
      if (iVar4 < 0) break;
      uStack_4c = *(undefined4 *)(DAT_004cfa40 + 4);
      uStack_48 = *(undefined4 *)(DAT_004cfa40 + 8);
      piVar10 = &local_50;
      uVar6 = DAT_004cfa44;
      local_50 = param_1;
      iVar4 = FUN_004cb968(param_1,&local_44,auStack_2c,DAT_004cf474,DAT_004cfa48,0,DAT_004cfa44,
                           piVar10);
      if (iVar4 < 0) break;
      if ((iVar4 != 0) && (iVar4 = FUN_004cae74(iVar4), iVar4 == 0)) {
        *(undefined4 *)(param_1 + 0x20) = local_44;
        *(undefined4 *)(param_1 + 0x24) = local_40;
        iVar4 = FUN_004cb3c8(param_1,&local_44,uVar7,DAT_004cfa4c,&local_68);
        if (iVar4 < 0) break;
        FUN_004cb016(&local_68);
        uVar1 = local_68;
        uVar8 = local_68 >> 0x10;
        uVar5 = lfs_fs_disk_version_major(param_1);
        if ((uVar1 >> 0x10 != uVar5) ||
           (uVar5 = lfs_fs_disk_version_minor(param_1), uVar5 < (uVar1 & 0xffff))) {
          uVar2 = lfs_fs_disk_version_minor(param_1);
          uVar3 = lfs_fs_disk_version_major(param_1);
          FUN_004733ee(DAT_004cfacc,DAT_004cfa2c,0x11b9,uVar8,uVar1 & 0xffff,uVar3,uVar2,
                       &DAT_004cf27c);
          iVar4 = -0x16;
          break;
        }
        uVar5 = lfs_fs_disk_version_minor(param_1);
        bVar9 = (uVar1 & 0xffff) < uVar5;
        if (bVar9) {
          uVar6 = lfs_fs_disk_version_minor(param_1);
          uVar2 = lfs_fs_disk_version_major(param_1);
          piVar10 = (int *)&DAT_004cf27c;
          uVar6 = uVar6 & 0xffff;
          FUN_004733ee(DAT_004cfa54,DAT_004cfa2c,0x11c8,uVar8,uVar1 & 0xffff,uVar2,uVar6,
                       &DAT_004cf27c);
        }
        FUN_004cf564(param_1,bVar9);
        if (local_5c != 0) {
          if (*(uint *)(param_1 + 0x70) < local_5c) {
            FUN_004733ee(DAT_004cfb00,DAT_004cfa2c,0x11d3,local_5c,*(undefined4 *)(param_1 + 0x70),
                         &DAT_004cf27c,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x70) = local_5c;
        }
        if (local_58 != 0) {
          if (*(uint *)(param_1 + 0x74) < local_58) {
            FUN_004733ee(DAT_004cfb04,DAT_004cfa2c,0x11de,local_58,*(undefined4 *)(param_1 + 0x74),
                         &DAT_004cf27c,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x74) = local_58;
        }
        if (local_54 != 0) {
          if (*(uint *)(param_1 + 0x78) < local_54) {
            FUN_004733ee(DAT_004cfb38,DAT_004cfa2c,0x11e9,local_54,*(undefined4 *)(param_1 + 0x78),
                         &DAT_004cf27c,uVar6,piVar10);
            iVar4 = -0x16;
            break;
          }
          *(uint *)(param_1 + 0x78) = local_54;
          uVar7 = lfs_min(*(undefined4 *)(param_1 + 0x7c),*(undefined4 *)(param_1 + 0x78));
          *(undefined4 *)(param_1 + 0x7c) = uVar7;
        }
        if ((*(int *)(*(int *)(param_1 + 0x68) + 0x20) != 0) &&
           (local_60 != *(int *)(*(int *)(param_1 + 0x68) + 0x20))) {
          FUN_004733ee(DAT_004cfb3c,DAT_004cfa2c,0x11f8,local_60,
                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x20),&DAT_004cf27c,uVar6,piVar10)
          ;
          iVar4 = -0x16;
          break;
        }
        *(int *)(param_1 + 0x6c) = local_60;
        if (local_64 != *(int *)(*(int *)(param_1 + 0x68) + 0x1c)) {
          FUN_004733ee(DAT_004cfb78,DAT_004cfa2c,0x1201,local_64,
                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x1c),&DAT_004cf27c,uVar6,piVar10)
          ;
          iVar4 = -0x16;
          break;
        }
      }
      iVar4 = FUN_004cbefc(param_1,&local_44,param_1 + 0x30);
    } while (iVar4 == 0);
    FUN_004cf274(param_1);
  }
  return iVar4;
}

