
undefined8 lfs_fs_disk_version_minor(void)

{
  ushort uVar1;
  undefined4 unaff_r7;
  
  uVar1 = lfs_fs_disk_version();
  return CONCAT44(unaff_r7,(uint)uVar1);
}

