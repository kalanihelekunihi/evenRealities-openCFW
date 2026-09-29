
uint lfs_tag_isvalid(uint param_1)

{
  return param_1 >> 0x1f ^ 1;
}

