
void FUN_005b7704(int param_1,ushort *param_2,int param_3,undefined4 param_4)

{
  undefined *puVar1;
  undefined *puVar2;
  undefined *puVar3;
  undefined *puVar4;
  undefined *puVar5;
  int iVar6;
  ushort uVar7;
  int iStack_1a8;
  undefined *puStack_1a4;
  int iStack_198;
  undefined *puStack_188;
  uint uStack_178;
  int iStack_174;
  int iStack_148;
  undefined *puStack_144;
  undefined *puStack_128;
  uint uStack_118;
  int iStack_114;
  int iStack_e8;
  undefined *puStack_e4;
  undefined *puStack_c8;
  uint uStack_b8;
  int iStack_b4;
  int iStack_88;
  undefined *puStack_84;
  undefined *puStack_68;
  uint uStack_58;
  int iStack_54;
  undefined4 uStack_28;
  
  uStack_28 = param_4;
  if ((param_1 == 0) ||
     (iVar6 = FUN_0043e2ea(param_1), puVar1 = PTR_FUN_005b7684_1_005b7920, iVar6 == 0)) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_1a4 = PTR_s_expand_animation_play__obj_is_in_005b7904;
      iStack_1a8 = 0x2f;
      FUN_0043d574(1,PTR_s_expand_anim_005b7910,PTR_s_D__01_workspace_s200_ap510b_iar__005b790c,
                   PTR_s_expand_animation_play_005b7908);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__expand_anim_expand_animation_pl_005b7914,
                          PTR_s__expand_anim_expand_animation_pl_005b7914);
    }
  }
  else if (param_2 == (ushort *)0x0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_1a4 = PTR_s_expand_animation_play__cfg_is_NU_005b7918;
      iStack_1a8 = 0x33;
      FUN_0043d574(1,PTR_s_expand_anim_005b7910,PTR_s_D__01_workspace_s200_ap510b_iar__005b790c,
                   PTR_s_expand_animation_play_005b7908);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__expand_anim_expand_animation_pl_005b791c,
                          PTR_s__expand_anim_expand_animation_pl_005b791c);
    }
  }
  else {
    FUN_00450500(param_1,PTR_FUN_005b7684_1_005b7920);
    puVar2 = PTR_FUN_005b76a4_1_005b7924;
    FUN_00450500(param_1,PTR_FUN_005b76a4_1_005b7924);
    puVar3 = PTR_FUN_005b76c4_1_005b7928;
    FUN_00450500(param_1,PTR_FUN_005b76c4_1_005b7928);
    puVar4 = PTR_FUN_005b76e4_1_005b792c;
    FUN_00450500(param_1,PTR_FUN_005b76e4_1_005b792c);
    FUN_0043f09a(param_1,*(undefined4 *)(param_2 + 2),*(undefined4 *)(param_2 + 6));
    FUN_0043f4c0(param_1,*(undefined4 *)(param_2 + 10),*(undefined4 *)(param_2 + 0xe));
    if (*param_2 == 0) {
      uVar7 = 0xfa;
    }
    else {
      uVar7 = *param_2;
    }
    FUN_004503d6(&iStack_88);
    iStack_88 = param_1;
    FUN_004506ce(&iStack_88,*(undefined4 *)(param_2 + 2),*(undefined4 *)(param_2 + 4));
    puVar5 = PTR_LAB_00450672_1_005b7930;
    uStack_58 = (uint)uVar7;
    puStack_84 = puVar3;
    puStack_68 = PTR_LAB_00450672_1_005b7930;
    iStack_54 = -(uint)param_2[1];
    FUN_00450408(&iStack_88);
    FUN_004503d6(&iStack_e8);
    iStack_e8 = param_1;
    FUN_004506ce(&iStack_e8,*(undefined4 *)(param_2 + 6),*(undefined4 *)(param_2 + 8));
    uStack_b8 = (uint)uVar7;
    puStack_e4 = puVar4;
    puStack_c8 = puVar5;
    iStack_b4 = -(uint)param_2[1];
    FUN_00450408(&iStack_e8);
    FUN_004503d6(&iStack_148);
    iStack_148 = param_1;
    FUN_004506ce(&iStack_148,*(undefined4 *)(param_2 + 10),*(undefined4 *)(param_2 + 0xc));
    uStack_118 = (uint)uVar7;
    puStack_144 = puVar1;
    puStack_128 = puVar5;
    iStack_114 = -(uint)param_2[1];
    FUN_00450408(&iStack_148);
    FUN_004503d6(&iStack_1a8);
    iStack_1a8 = param_1;
    FUN_004506ce(&iStack_1a8,*(undefined4 *)(param_2 + 0xe),*(undefined4 *)(param_2 + 0x10));
    uStack_178 = (uint)uVar7;
    puStack_1a4 = puVar2;
    puStack_188 = puVar5;
    iStack_174 = -(uint)param_2[1];
    if (param_3 != 0) {
      iStack_198 = param_3;
    }
    FUN_00450408(&iStack_1a8);
  }
  return;
}

