
void FUN_10004478(undefined4 param_1,uint param_2,undefined4 param_3)

{
  undefined *puVar1;
  int iVar2;
  
  if (param_2 < 1000) {
    FUN_100061a4(PTR_s_level_timout_invalid_100044f8);
    return;
  }
  FUN_10004a48(0x18,1);
  puVar1 = PTR_LAB_100044f4;
  uRam00000004 = 0;
  iVar2 = 0x10;
  do {
    if (param_2 / 1000 <= (uint)((1 << (uRam00000004 + 0x10 & 0x3f)) / 1000000)) {
      uRam00000004 = uRam00000004 | uRam00000004 << 4;
      goto LAB_100044be;
    }
    uRam00000004 = uRam00000004 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  uRam00000004 = 0xff;
LAB_100044be:
  uRam0000000c = 0x76;
  *DAT_100044f0 = param_3;
  FUN_100030e8(0xb,puVar1,0);
  uRam00000000 = uRam00000000 | 1;
  return;
}

