
undefined8 EvenAI_InputEventWarp(char *param_1,int param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 unaff_r5;
  
  if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x2b0;
      FUN_0043d574(2,DAT_004e5fa0,DAT_004e5f9c,DAT_004e64b0,0x2b0,DAT_004e64ac);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004e654c,DAT_004e654c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (*param_1 == '\x04') {
      cVar1 = param_1[1];
      if (cVar1 != '\n') {
        if (cVar1 == 'D') {
          even_ai_scroll_by_delta(1,(int)*(short *)(param_1 + 4),(int)*(short *)(param_1 + 2));
        }
        else if (cVar1 == 'E') {
          even_ai_scroll_by_delta
                    (0xffffffff,(int)*(short *)(param_1 + 4),(int)*(short *)(param_1 + 2));
        }
        else if ((cVar1 == 'H') && (iVar2 = FUN_0045a568(), iVar2 == 1)) {
          FUN_00464c36(7,0,0,0);
        }
      }
    }
    uVar3 = 0;
  }
  return CONCAT44(unaff_r5,uVar3);
}

