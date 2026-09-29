
undefined4
even_ai_common_timer_mgr_start
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  
  cVar2 = FUN_0045a568();
  puVar1 = DAT_004e3130;
  if (cVar2 == '\x01') {
    uVar3 = osKernelGetTickCount();
    *puVar1 = uVar3;
    puVar1[1] = param_1;
    *(undefined1 *)(puVar1 + 2) = 1;
    *(undefined1 *)((int)puVar1 + 9) = 1;
  }
  return param_4;
}

