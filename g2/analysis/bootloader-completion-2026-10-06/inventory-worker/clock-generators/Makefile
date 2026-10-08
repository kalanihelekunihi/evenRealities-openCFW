ROOT := ../../../../..
PYTHON ?= /Users/kalani/.local/share/opencfw/venv/bin/python
OUT ?= /tmp/opencfw-clock-generators
SOURCE := $(ROOT)/g2/components/bootloader/initializer_callbacks/clock_generators.c
all:
	clang --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffreestanding -fno-builtin -c $(SOURCE) -o $(OUT).o
	arm-none-eabi-ld -T module.ld $(OUT).o -o $(OUT).elf
verify: all
	$(PYTHON) verify.py --elf $(OUT).elf --output comparison.json
native:
	clang --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -ffreestanding -fno-builtin -c $(SOURCE) -o $(OUT).o
	clang --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -ffreestanding -fno-builtin -c $(ROOT)/g2/components/bootloader/initializer_callbacks/clock_pll_math.c -o $(OUT)-math.o
	clang --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -ffreestanding -fno-builtin -c $(ROOT)/g2/components/bootloader/initializer_callbacks/clock_pll_rounding.c -o $(OUT)-rounding.o
	clang --target=arm-none-eabi -mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -O0 -ffp-contract=off -ffreestanding -fno-builtin -c $(ROOT)/g2/components/bootloader/initializer_callbacks/clock_pll_mod.c -o $(OUT)-mod.o
	arm-none-eabi-ld -T native-module.ld $(OUT).o $(OUT)-math.o $(OUT)-rounding.o $(OUT)-mod.o -o $(OUT)-native.elf
verify-native: native
	$(PYTHON) verify_math.py --elf $(OUT)-native.elf --output math-comparison.json
