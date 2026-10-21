SECTIONS
{
  .data.opencfw.codec.clock_pin_0a 0x20000114 : { KEEP(*(.data.opencfw.codec.clock_pin_0a)) }
  .data.opencfw.codec.clock_pin_0d 0x20000118 : { KEEP(*(.data.opencfw.codec.clock_pin_0d)) }
  .data.opencfw.codec.clock_pin_0b 0x2000011c : { KEEP(*(.data.opencfw.codec.clock_pin_0b)) }
  .data.opencfw.codec.clock_pin_0c 0x20000120 : { KEEP(*(.data.opencfw.codec.clock_pin_0c)) }
  .data.opencfw.codec.clock_pin_1a 0x20000124 : { KEEP(*(.data.opencfw.codec.clock_pin_1a)) }
  .data.opencfw.codec.clock_pin_1d 0x20000128 : { KEEP(*(.data.opencfw.codec.clock_pin_1d)) }
  .data.opencfw.codec.clock_pin_1e 0x2000012c : { KEEP(*(.data.opencfw.codec.clock_pin_1e)) }
  .data.opencfw.codec.clock_pin_1b 0x20000130 : { KEEP(*(.data.opencfw.codec.clock_pin_1b)) }
  .data.opencfw.codec.clock_pin_1c 0x20000134 : { KEEP(*(.data.opencfw.codec.clock_pin_1c)) }
}
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_0a) == 4, "pin 0a extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_0d) == 4, "pin 0d extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_0b) == 4, "pin 0b extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_0c) == 4, "pin 0c extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_1a) == 4, "pin 1a extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_1d) == 4, "pin 1d extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_1e) == 4, "pin 1e extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_1b) == 4, "pin 1b extent")
ASSERT(SIZEOF(.data.opencfw.codec.clock_pin_1c) == 4, "pin 1c extent")
