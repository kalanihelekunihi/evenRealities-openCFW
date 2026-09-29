
undefined8 text_stream_animation_preset_get(byte param_1)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  if ((*DAT_00553d44 == '\0') || (3 < param_1)) {
    uVar1 = 0;
  }
  else if (*(int *)(DAT_00553ff0 + (uint)param_1 * 4) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_00463e9a(*(undefined4 *)(DAT_00553ff0 + (uint)param_1 * 4));
  }
  return CONCAT44(unaff_r7,uVar1);
}

