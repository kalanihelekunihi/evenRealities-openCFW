
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00502dc2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  
  puVar1 = _DAT_0050324c;
  *_DAT_0050324c = 0;
  puVar4 = puVar1;
  if ((param_1 << 0x1f < 0) &&
     (iVar2 = func_0x0047344e(puVar1,0x60,0x502ef0,PTR_s_SLIDER_EVENT_PRESS_00503250), 0 < iVar2)) {
    if (0x5f < iVar2) {
      iVar2 = 0x60;
    }
    puVar4 = puVar1 + iVar2;
  }
  if ((param_1 << 0x1e < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_RELEASE_00503254), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x1d < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_SINGLE_00503258), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x1c < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_DOUBLE_0050325c), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x1b < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_LONG_00503260), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x1a < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_SLIDE_L_00503264), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x19 < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_SLIDE_R_00503268), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((param_1 << 0x18 < 0) &&
     (puVar3 = (undefined1 *)
               func_0x0047344e(puVar4,puVar1 + (0x60 - (int)puVar4),0x502ef0,
                               PTR_s_SLIDER_EVENT_ERROR_0050326c), 0 < (int)puVar3)) {
    if ((int)(puVar1 + (0x60 - (int)puVar4)) <= (int)puVar3) {
      puVar3 = puVar1 + (0x60 - (int)puVar4);
    }
    puVar4 = puVar4 + (int)puVar3;
  }
  if ((puVar1 < puVar4) && (puVar4[-1] == '|')) {
    puVar4[-1] = 0;
  }
  return CONCAT44(param_4,puVar1);
}

