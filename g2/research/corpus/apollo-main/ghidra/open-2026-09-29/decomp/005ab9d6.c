
undefined4
af_autofitter_load_glyph
          (int param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5)

{
  undefined4 uVar1;
  undefined1 auStack_1a34 [60];
  undefined1 auStack_19f8 [6632];
  
  af_glyph_hints_init(auStack_19f8,**(undefined4 **)(param_1 + 4));
  af_loader_init(auStack_1a34,auStack_19f8);
  uVar1 = af_loader_load_glyph(auStack_1a34,param_1,*(undefined4 *)(param_2 + 4),param_4,param_5);
  af_loader_done(auStack_1a34);
  af_glyph_hints_done(auStack_19f8);
  return uVar1;
}

