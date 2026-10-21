/* Loaded image-B clock tables from pinned NationalChip Grus clk_priv.h.
 * The 26 module records were independently checked field by field against
 * native initialized data by verify_clk_table.py (26/26).
 * Copyright belongs to NationalChip SDK contributors; retain SDK license.
 */
#include <stddef.h>
#include <stdint.h>
#include <driver/gx_clock/gx_clock_v2.h>

typedef struct {
    GX_CLOCK_MODULE mod;
    int8_t gate_high_offs;
    int8_t gate_all_offs;
    int8_t clk_offs;
    GX_CLOCK_DIV *div;
    GX_CLOCK_DTO *dto;
} image_b_clock_module_param;

_Static_assert(sizeof(GX_CLOCK_DIV) == 4, "clock div layout");
_Static_assert(sizeof(GX_CLOCK_DTO) == 1, "clock dto layout");
_Static_assert(sizeof(image_b_clock_module_param) == 16, "clock row layout");

GX_CLOCK_DIV gx8002_image_b_clock_div_table_10016b40[] = {
	{.addr = 0x80, .offs =  8, .mask =  0x3f}, // CLOCK_MODULE_RTC
	{.addr = 0x80, .offs = 16, .mask =  0x3f}, // CLOCK_MODULE_PMU
	{.addr = 0x80, .offs = 24, .mask =  0x3f}, // CLOCK_MODULE_AUDIO_IN_SYS
	{.addr = 0x84, .offs = 16, .mask =  0x3f}, // CLOCK_MODULE_FFT
	{.addr = 0x84, .offs = 24, .mask =  0x3f}, // CLOCK_MODULE_GPIO
	{.addr = 0x84, .offs =  0, .mask =  0x3f}, // CLOCK_MODULE_HW_I2C
	{.addr = 0x80, .offs =  0, .mask =  0x3f}, // CLOCK_MODULE_SRAM
	{.addr = 0x88, .offs =  0, .mask = 0x3ff}, // CLOCK_MODULE_AUDIO_IN_ADC
	{.addr = 0x84, .offs =  8, .mask =  0x3f}, // CLOCK_MODULE_AUDIO_IN_PDM
	{.addr = 0x88, .offs = 12, .mask =  0x3f}, // CLOCK_MODULE_OSC_REF

	{.addr = 0x84, .offs = 16, .mask =  0x3f}, // CLOCK_MODULE_SCPU
	{.addr = 0x80, .offs =  8, .mask =  0x3f}, // CLOCK_MODULE_I2C0_I2C1
	{.addr = 0x84, .offs =  8, .mask =  0x3f}, // CLOCK_MODULE_NPU
	{.addr = 0x80, .offs = 16, .mask =  0x3f}, // CLOCK_MODULE_FLASH_SPI
	{.addr = 0x80, .offs = 24, .mask =  0x3f}, // CLOCK_MODULE_GENERAL_SPI
	{.addr = 0x84, .offs =  0, .mask =  0x3f}, // CLOCK_MODULE_AUDIO_LODAC
	{.addr = 0x80, .offs =  0, .mask =  0x3f}, // CLOCK_MODULE_TIMER_WDT
};

GX_CLOCK_DTO gx8002_image_b_clock_dto_table_10016b3c[] = {
	{.addr = 0x24}, // CLOCK_MODULE_AUDIO_IN_SYS
	{.addr = 0x24}, // CLOCK_MODULE_UART0_UART1
	{.addr = 0x28}, // CLOCK_MODULE_AUDIO_PLAY
};

image_b_clock_module_param gx8002_image_b_clock_param_table_1001699c[] = {
	/*  Mod                    HGate AGate Clk             Div                     Dto         */
	{CLOCK_MODULE_RTC         ,  0 ,  1 ,  1 , gx8002_image_b_clock_div_table_10016b40 +  0 , NULL                  },
	{CLOCK_MODULE_PMU         ,  2 ,  3 ,  3 , gx8002_image_b_clock_div_table_10016b40 +  1 , NULL                  },
	{CLOCK_MODULE_AUDIO_IN_SYS,  4 ,  5 ,  6 , gx8002_image_b_clock_div_table_10016b40 +  2 , gx8002_image_b_clock_dto_table_10016b3c + 0},
	{CLOCK_MODULE_FFT         ,  7 ,  8 ,  9 , gx8002_image_b_clock_div_table_10016b40 +  3 , NULL                  },
	{CLOCK_MODULE_GPIO        ,  9 , 10 , 10 , gx8002_image_b_clock_div_table_10016b40 +  4 , NULL                  },
	{CLOCK_MODULE_HW_I2C      , 11 , 12 , 11 , gx8002_image_b_clock_div_table_10016b40 +  5 , NULL                  },
	{CLOCK_MODULE_SRAM        , 13 , 14 , 12 , gx8002_image_b_clock_div_table_10016b40 +  6 , NULL                  },
	{CLOCK_MODULE_AUDIO_IN_ADC,  4 ,  6 , 19 , gx8002_image_b_clock_div_table_10016b40 +  7 , NULL                  },
	{CLOCK_MODULE_AUDIO_IN_PDM,  4 , 19 , 20 , gx8002_image_b_clock_div_table_10016b40 +  8 , NULL                  },
	{CLOCK_MODULE_OSC_REF     , 20 , 21 , 24 , gx8002_image_b_clock_div_table_10016b40 +  9 , NULL                  },

	{CLOCK_MODULE_SCPU        ,  4 , 12 ,  0 , gx8002_image_b_clock_div_table_10016b40 + 10 , NULL                  },
	{CLOCK_MODULE_UART0_UART1 ,  5 ,  5 ,  1 , NULL                    , gx8002_image_b_clock_dto_table_10016b3c + 1},
	{CLOCK_MODULE_UART0       ,  5 , 24 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_UART1       ,  5 , 25 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_AUDIO_PLAY  ,  6 , 26 ,  2 , NULL                    , gx8002_image_b_clock_dto_table_10016b3c + 2},
	{CLOCK_MODULE_I2C0_I2C1   ,  7 ,  7 ,  3 , gx8002_image_b_clock_div_table_10016b40 + 11 , NULL                  },
	{CLOCK_MODULE_I2C0        ,  7 , 28 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_I2C1        ,  7 , 29 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_NPU         ,  8 ,  8 ,  4 , gx8002_image_b_clock_div_table_10016b40 + 12 , NULL                  },
	{CLOCK_MODULE_FLASH_SPI   ,  9 ,  9 ,  5 , gx8002_image_b_clock_div_table_10016b40 + 13 , NULL                  },
	{CLOCK_MODULE_GENERAL_SPI , 10 , 10 ,  6 , gx8002_image_b_clock_div_table_10016b40 + 14 , NULL                  },
	{CLOCK_MODULE_AUDIO_LODAC , 11 , 11 ,  7 , gx8002_image_b_clock_div_table_10016b40 + 15 , NULL                  },
	{CLOCK_MODULE_TIMER_WDT   , 27 , 27 , 11 , gx8002_image_b_clock_div_table_10016b40 + 16 , NULL                  },
	{CLOCK_MODULE_TIMER       , 27 , 22 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_WDT         , 27 , 23 , -1 , NULL                    , NULL                  },
	{CLOCK_MODULE_DMA         , -1 , 14 , -1 , NULL                    , NULL                  },
};
