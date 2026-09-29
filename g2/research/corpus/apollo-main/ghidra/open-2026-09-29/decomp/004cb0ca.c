
undefined8 lfs_fs_disk_version_major(void)

{
  uint uVar1;
  undefined4 unaff_r7;
  
  uVar1 = lfs_fs_disk_version();
  return CONCAT44(unaff_r7,uVar1 >> 0x10);
}

