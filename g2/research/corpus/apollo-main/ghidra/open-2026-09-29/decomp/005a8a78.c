
void af_latin_metrics_init_widths(int *param_1,int param_2)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  char *pcVar8;
  uint local_6298;
  uint local_6294;
  undefined1 auStack_6290 [4];
  int local_628c;
  undefined4 local_6288;
  undefined4 local_6284;
  undefined4 local_6280;
  undefined4 local_627c;
  undefined1 local_6278;
  undefined4 local_6274;
  uint local_6268;
  undefined1 auStack_1a04 [44];
  uint local_19d8 [1647];
  
  af_glyph_hints_init(auStack_1a04,*(undefined4 *)(param_2 + 100));
  param_1[0xd] = 0;
  param_1[0x919] = 0;
  pcVar8 = *(char **)(*(int *)(DAT_005a96f4 + (uint)*(byte *)(*param_1 + 2) * 4) + 0x10);
  uVar1 = af_shaper_buf_create(param_2);
  iVar6 = 0;
  do {
    do {
      if (*pcVar8 == '\0') goto LAB_005a8afc;
      for (; *pcVar8 == ' '; pcVar8 = pcVar8 + 1) {
      }
      pcVar8 = (char *)af_shaper_get_cluster(pcVar8,param_1,uVar1,&local_6294);
    } while (1 < local_6294);
    local_6298 = 0;
    iVar6 = af_shaper_get_elem(param_1,uVar1,0,0);
  } while (iVar6 == 0);
LAB_005a8afc:
  af_shaper_buf_destroy(param_2,uVar1);
  if (((iVar6 != 0) && (iVar6 = FT_Load_Glyph(param_2,iVar6,1), iVar6 == 0)) &&
     (0 < *(short *)(*(int *)(param_2 + 0x54) + 0x6e))) {
    FUN_0043c0e4(auStack_6290,0x488c,0);
    local_6268 = param_1[10];
    local_6288 = 0x10000;
    local_6284 = 0x10000;
    local_6280 = 0;
    local_627c = 0;
    local_6278 = 0;
    local_6274 = 0;
    local_628c = param_2;
    af_glyph_hints_rescale(auStack_1a04,auStack_6290);
    iVar6 = af_glyph_hints_reload(auStack_1a04,*(int *)(param_2 + 0x54) + 0x6c);
    if (iVar6 == 0) {
      for (uVar7 = 0; (int)uVar7 < 2; uVar7 = uVar7 + 1) {
        local_6298 = 0;
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
            if (local_6298 < 0x10) {
              param_1[uVar7 * 0x90c + local_6298 * 3 + 0xe] = iVar6;
              local_6298 = local_6298 + 1;
            }
          }
        }
        af_sort_and_quantize_widths(&local_6298,param_1 + uVar7 * 0x90c + 0xe,local_6268 / 100);
        param_1[uVar7 * 0x90c + 0xd] = local_6298;
      }
    }
  }
  for (iVar6 = 0; iVar6 < 2; iVar6 = iVar6 + 1) {
    if (param_1[iVar6 * 0x90c + 0xd] == 0) {
      iVar3 = (param_1[10] * 0x32) / 0x800;
    }
    else {
      iVar3 = param_1[iVar6 * 0x90c + 0xe];
    }
    param_1[iVar6 * 0x90c + 0x3e] = iVar3 / 5;
    param_1[iVar6 * 0x90c + 0x3f] = iVar3;
    *(undefined1 *)(param_1 + iVar6 * 0x90c + 0x40) = 0;
  }
  af_glyph_hints_done(auStack_1a04);
  return;
}

