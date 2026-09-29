
undefined4 even_ai_stream_event_forward(int param_1,int param_2)

{
  undefined4 *puVar1;
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined1 local_24;
  undefined1 local_23;
  undefined1 local_20;
  undefined1 local_1f;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined1 local_18;
  undefined1 local_17;
  undefined1 local_16;
  undefined1 local_15;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_10;
  undefined1 local_f;
  undefined1 local_e;
  undefined1 local_d;
  undefined1 local_c;
  undefined1 local_b;
  
  if (param_1 == 10) {
    local_10 = 4;
    local_f = 10;
    local_e = 0;
    local_d = 0;
    local_c = 0;
    local_b = 0;
    FUN_00464bb2(7,&local_10,6,0);
  }
  else if (param_1 == 0x48) {
    local_18 = 4;
    local_17 = 0x48;
    local_16 = 0;
    local_15 = 0;
    local_14 = 0;
    local_13 = 0;
    FUN_00464bb2(7,&local_18,6,0);
  }
  else if (param_1 == 0x45) {
    puVar1 = *(undefined4 **)(param_2 + 0x10);
    local_20 = 4;
    local_1f = 0x45;
    local_1e = (undefined1)*puVar1;
    local_1d = (undefined1)((uint)*puVar1 >> 8);
    local_1c = (undefined1)puVar1[1];
    local_1b = (undefined1)((uint)puVar1[1] >> 8);
    FUN_00464bb2(7,&local_20,6,0);
  }
  else if (param_1 == 0x44) {
    puVar1 = *(undefined4 **)(param_2 + 0x10);
    local_28 = 4;
    local_27 = 0x44;
    local_26 = (undefined1)*puVar1;
    local_25 = (undefined1)((uint)*puVar1 >> 8);
    local_24 = (undefined1)puVar1[1];
    local_23 = (undefined1)((uint)puVar1[1] >> 8);
    FUN_00464bb2(7,&local_28,6,0);
  }
  return 0;
}

