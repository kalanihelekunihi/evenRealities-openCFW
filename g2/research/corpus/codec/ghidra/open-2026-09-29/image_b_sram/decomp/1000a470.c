
/* WARNING: Removing unreachable block (ram,0x1000a4fc) */
/* WARNING: Removing unreachable block (ram,0x1000a55c) */
/* WARNING: Removing unreachable block (ram,0x1000a564) */
/* WARNING: Removing unreachable block (ram,0x1000a506) */
/* WARNING: Removing unreachable block (ram,0x1000a602) */
/* WARNING: Removing unreachable block (ram,0x1000a60c) */
/* WARNING: Removing unreachable block (ram,0x1000a612) */
/* WARNING: Removing unreachable block (ram,0x1000a514) */
/* WARNING: Removing unreachable block (ram,0x1000a68a) */

bool FUN_1000a470(void)

{
  int iVar1;
  bool bVar2;
  uint uVar3;
  uint local_20;
  uint uStack_1c;
  uint uStack_18;
  ushort uStack_14;
  
  FUN_10005cb0();
  iVar1 = DAT_1000a704;
  if (*(int *)(DAT_1000a704 + 4) != 4) {
    *(undefined4 *)(DAT_1000a704 + 4) = 4;
    gx_audio_in_set_fftvad_curve_1(0x4cd,0xf00);
    gx_audio_in_set_fftvad_curve_2(0x4cd,0x500);
    FUN_10005b9c(0x4cd,0x1000);
    gx_audio_in_set_fftvad_curve_4(0xa00,0x400);
    gx_audio_in_set_fftvad_curve_5(0xc00);
    local_20 = 0x106028f;
    uStack_1c = 0x210083;
    gx_audio_in_set_fftvad_chipping(0x106028f,0x210083);
    gx_audio_in_set_fftvad_w(3);
  }
  gx_audio_in_get_fftvad_state(&local_20);
  uVar3 = (uStack_14 + 0x5e) % 0x5f;
  if (uVar3 < 0x20) {
    bVar2 = (1 << (uVar3 & 0x3f) & local_20) != 0;
  }
  else if (uVar3 < 0x40) {
    bVar2 = (1 << (uVar3 - 0x20 & 0x3f) & uStack_1c) != 0;
  }
  else {
    bVar2 = (1 << (uVar3 - 0x40 & 0x3f) & uStack_18) != 0;
  }
  if (*(int *)(iVar1 + 4) == 1) {
    bVar2 = true;
  }
  return bVar2;
}

