
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 even_ai_page_init(undefined4 param_1,undefined4 param_2,undefined *param_3)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined *puVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  uint uVar8;
  undefined4 uStack_20;
  undefined *puStack_1c;
  
  piVar2 = _DAT_004e7530;
  if (*_DAT_004e7530 == 0) {
    iVar5 = ui_common_api_fn_00509c1c();
    *piVar2 = iVar5;
  }
  *_DAT_004e7594 = 0;
  even_ai_listening_visibility_set(0);
  FUN_0043f506(param_1,0x240);
  FUN_0043f568(param_1,0x120);
  FUN_0043f0e0(param_1,0);
  FUN_0043f142(param_1,0);
  FUN_0043ded4(param_1,0x50000);
  FUN_0043dfa4(param_1,0xb014);
  FUN_0044e368(param_1,0);
  FUN_0044146a(param_1,0,0);
  uVar6 = FUN_0044104c(0);
  FUN_0044127e(param_1,uVar6,0);
  FUN_0044129e(param_1,0,0);
  FUN_0044131c(param_1,0,0);
  even_ai_style_apply(param_1,0,0);
  puVar1 = DAT_004e74fc;
  uVar6 = FUN_0043de82(param_1);
  *puVar1 = uVar6;
  FUN_0043f506(*puVar1,0x240);
  FUN_0043f568(*puVar1,0x3fffffff);
  FUN_004411aa(*puVar1,0x100,0);
  FUN_0043f6b8(*puVar1,4,0,0);
  FUN_0044131c(*puVar1,0,0);
  uVar6 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar6,0);
  FUN_0044129e(*puVar1,0xff,0);
  FUN_0044146a(*puVar1,0,0);
  even_ai_style_apply(*puVar1,0,0);
  FUN_0044121c(*puVar1,0x10,0);
  FUN_0043dfa4(*puVar1,0x12);
  uVar6 = 8;
  cVar4 = FUN_0045a568();
  if (cVar4 == '\x01') {
    uVar6 = 0xfffffff8;
  }
  uVar7 = FUN_0043de82(*puVar1);
  puVar1[1] = uVar7;
  FUN_0043f506(puVar1[1],0x230);
  FUN_0043f568(puVar1[1],0x3fffffff);
  FUN_004411aa(puVar1[1],0xf0,0);
  FUN_0043f6b8(puVar1[1],2,uVar6,0);
  FUN_0044131c(puVar1[1],1,0);
  uVar7 = FUN_0044104c(0xffffff);
  FUN_004412ec(puVar1[1],uVar7,0);
  FUN_0044146a(puVar1[1],6,0);
  uVar7 = FUN_0044104c(0);
  FUN_0044127e(puVar1[1],uVar7,0);
  FUN_0044129e(puVar1[1],0xff,0);
  FUN_0044120e(puVar1[1],0x10,0);
  FUN_0044121c(puVar1[1],0x18,0);
  FUN_0044122a(puVar1[1],0x14,0);
  FUN_00441238(puVar1[1],0,0);
  FUN_0043dfa4(puVar1[1],0x12);
  uVar7 = FUN_0043de82(puVar1[1]);
  puVar1[2] = uVar7;
  FUN_0043f506(puVar1[2],0x21c);
  FUN_0043f568(puVar1[2],0x3fffffff);
  FUN_004411aa(puVar1[2],200,0);
  FUN_0043f6b8(puVar1[2],1,0,0);
  FUN_0044131c(puVar1[2],0,0);
  FUN_0044146a(puVar1[2],0,0);
  uVar7 = FUN_0044104c(0);
  FUN_0044127e(puVar1[2],uVar7,0);
  FUN_0044129e(puVar1[2],0xff,0);
  even_ai_style_apply(puVar1[2],0,0);
  FUN_0044e368(puVar1[2],3);
  FUN_0044e3ca(puVar1[2],0xc);
  FUN_0043ded4(puVar1[2],0x10);
  FUN_0043dfa4(puVar1[2],0x300);
  FUN_00451740(puVar1[2],_DAT_004e7598,0xe,0);
  uVar7 = FUN_00499416(puVar1[1]);
  puVar1[3] = uVar7;
  FUN_0043f506(puVar1[3],0x20b);
  FUN_0043f568(puVar1[3],0x1e);
  FUN_0043f6b8(puVar1[3],1,0,0);
  FUN_0044145a(puVar1[3],2,0);
  uVar7 = FUN_0044104c(0xffffff);
  FUN_0044140e(puVar1[3],uVar7,0);
  FUN_0044143e(puVar1[3],*_DAT_004e759c,0);
  FUN_0044131c(puVar1[3],0,0);
  even_ai_style_apply(puVar1[3],0,0);
  FUN_0043dfa4(puVar1[3],0x12);
  puVar3 = PTR_s_ID_EVEN_AI_LISTENING_004e75a0;
  uVar7 = FUN_00460084(PTR_s_ID_EVEN_AI_LISTENING_004e75a0);
  uVar7 = FUN_0045fffe(puVar3,uVar7);
  FUN_0049942e(puVar1[3],uVar7);
  iVar5 = text_stream_animation_presets_init(*puVar1,1);
  uStack_20 = param_2;
  puStack_1c = param_3;
  if (iVar5 == 0) {
    for (uVar8 = 0; (int)uVar8 < 4; uVar8 = uVar8 + 1) {
      iVar5 = text_stream_animation_preset_get(uVar8 & 0xff);
      if (iVar5 != 0) {
        FUN_0043f6b8(iVar5,5,uVar6,9);
      }
    }
    FUN_005537cc(0);
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      puStack_1c = PTR_s_Failed_to_initialize_EvenAI_anim_004e75a4;
      uStack_20 = 0x9da;
      FUN_0043d574(2,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                   PTR_s_even_ai_page_init_004e75a8);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__even_ai_ui_Failed_to_initialize_004e75ac);
    }
  }
  return CONCAT44(puStack_1c,uStack_20);
}

