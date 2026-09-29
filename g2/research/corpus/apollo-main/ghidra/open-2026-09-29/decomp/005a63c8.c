
void af_cjk_metrics_init_widths(int *param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  char *pcVar8;
  uint local_52e8;
  uint local_52e4;
  undefined1 auStack_52e0 [4];
  int local_52dc;
  undefined4 local_52d8;
  undefined4 local_52d4;
  undefined4 local_52d0;
  undefined4 local_52cc;
  undefined1 local_52c8;
  undefined4 local_52c4;
  uint local_52b8;
  undefined1 auStack_1a04 [44];
  uint local_19d8 [1647];
  
  af_glyph_hints_init(auStack_1a04,*(undefined4 *)(param_2 + 100));
  param_1[0xd] = 0;
  param_1[0x723] = 0;
  pcVar8 = *(char **)(*(int *)(DAT_005a691c + (uint)*(byte *)(*param_1 + 2) * 4) + 0x10);
  uVar1 = af_shaper_buf_create(param_2);
  iVar6 = 0;
  do {
    do {
      if (*pcVar8 == '\0') goto LAB_005a644c;
      for (; *pcVar8 == ' '; pcVar8 = pcVar8 + 1) {
      }
      pcVar8 = (char *)af_shaper_get_cluster(pcVar8,param_1,uVar1,&local_52e4);
    } while (1 < local_52e4);
    local_52e8 = 0;
    iVar6 = af_shaper_get_elem(param_1,uVar1,0,0);
  } while (iVar6 == 0);
LAB_005a644c:
  af_shaper_buf_destroy(param_2,uVar1);
  if ((((iVar6 != 0) && (iVar6 != 0)) && (iVar6 = FT_Load_Glyph(param_2,iVar6,1), iVar6 == 0)) &&
     (0 < *(short *)(*(int *)(param_2 + 0x54) + 0x6e))) {
    FUN_0043c0e4(auStack_52e0,0x38dc,0);
    local_52b8 = param_1[10];
    local_52d8 = 0x10000;
    local_52d4 = 0x10000;
    local_52d0 = 0;
    local_52cc = 0;
    local_52c8 = 0;
    local_52c4 = 0;
    local_52dc = param_2;
    af_glyph_hints_rescale(auStack_1a04,auStack_52e0);
    iVar6 = af_glyph_hints_reload(auStack_1a04,*(int *)(param_2 + 0x54) + 0x6c);
    if (iVar6 == 0) {
      for (uVar7 = 0; (int)uVar7 < 2; uVar7 = uVar7 + 1) {
        local_52e8 = 0;
        iVar6 = af_latin_hints_compute_segments(auStack_1a04,uVar7 & 0xff);
        if (iVar6 != 0) break;
        af_latin_hints_link_segments(auStack_1a04,0,0,uVar7 & 0xff);
        uVar4 = local_19d8[uVar7 * 0x151 + 2];
        uVar5 = local_19d8[uVar7 * 0x151] * 0x2c + uVar4;
        for (; uVar4 < uVar5; uVar4 = uVar4 + 0x2c) {
          uVar2 = *(uint *)(uVar4 + 0x14);
          if (((uVar2 != 0) && (*(uint *)(uVar2 + 0x14) == uVar4)) && (uVar4 < uVar2)) {
            iVar6 = (int)*(short *)(uVar4 + 2) - (int)*(short *)(uVar2 + 2);
            if (iVar6 < 0) {
              iVar6 = -iVar6;
            }
            if (local_52e8 < 0x10) {
              param_1[uVar7 * 0x716 + local_52e8 * 3 + 0xe] = iVar6;
              local_52e8 = local_52e8 + 1;
            }
          }
        }
        af_sort_and_quantize_widths(&local_52e8,param_1 + uVar7 * 0x716 + 0xe,local_52b8 / 100);
        param_1[uVar7 * 0x716 + 0xd] = local_52e8;
      }
    }
  }
  for (iVar6 = 0; iVar6 < 2; iVar6 = iVar6 + 1) {
    if (param_1[iVar6 * 0x716 + 0xd] == 0) {
      iVar3 = (param_1[10] * 0x32) / 0x800;
    }
    else {
      iVar3 = param_1[iVar6 * 0x716 + 0xe];
    }
    param_1[iVar6 * 0x716 + 0x3e] = iVar3 / 5;
    param_1[iVar6 * 0x716 + 0x3f] = iVar3;
    *(undefined1 *)(param_1 + iVar6 * 0x716 + 0x40) = 0;
  }
  af_glyph_hints_done(auStack_1a04);
  return;
}

