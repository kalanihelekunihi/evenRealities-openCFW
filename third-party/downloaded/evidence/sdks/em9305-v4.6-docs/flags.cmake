# Read the Architect generated flags for the ARC.
IF(MW_FOR_EM)
    SET(ARC_FLAGS
        -tcf=em9305
    )
ELSE()
    SET(ARC_FLAGS
        -tcf=${COMMON_DIR}/${TARGET_HW}/tool_config/arc.tcf
    )
ENDIF()

# Common compile flags for both C and assembly.
SET(COMPILE_FLAGS
    ${ARC_FLAGS}

    -Wall                    # Turn on all warnings.
    -Wconversion             # Warn on conversion (loss of precision).
    -Hhostlib=               # Specify the library to implement runtime system calls.
    -Hnocrt                  # Suppresses linking of runtime startup file.
    -Hon=Long_enums          # Needed for a bug in older compilers.
    -Hnocopyr                # Disables the compiler version and copyright.
    -Hnosdata                # Don't assume any variables are in the small-data area.
    -nostdsysteminc          # Do not use the standard include files.
    # -Os                      # Optimize for code size.
    -Hccm                    # Assume a closely-coupled memory system with distinct I and D spaces with no cross access.
    -mllvm                   # Additional arguments to forward to LLVM's option processing.
    -align-labels=false      # Disable alignment of labels.
    -Hnoivt                  # Turn off the auto stuff IVT feature of the compiler.
#    -g                       # Produce debugging information.
    -ffunction-sections      # This will prevent optimizations in the code where an address
    -fdata-sections          # may be re-used for multiple variables or functions.
    -Wl,-Bdefine:STACKSIZE=${STACKSIZE}
    -Wl,-Bdefine:HEAPSIZE=${HEAPSIZE}

    # Turn off these warnings (for now).
    -Wno-cast-align

    # Long jump
    -Mb
)

# check if default linker script is LLVM
execute_process(COMMAND ${CMAKE_ASM_COMPILER} -h
                    RESULT_VARIABLE CCAC_OPTION_RESULT
                    OUTPUT_VARIABLE CCAC_OPTION_OUTPUT)

IF("${CCAC_OPTION_OUTPUT}" MATCHES "-Hldac")
    SET(COMPILE_FLAGS
        ${COMPILE_FLAGS}
        -Hldac                    # Use the MetaWare linker instead of the LLVM linker.
    )
ENDIF()

IF(NOT LDRA_ENABLE)
    SET(COMPILE_FLAGS
        ${COMPILE_FLAGS}
        -Os                      # Optimize for code size.
    )
ENDIF()

# Add Werror flag if not compiled for SDK
IF((NOT SDK_BUILD) AND (NOT LDRA_ENABLE) )
SET(COMPILE_FLAGS
    ${COMPILE_FLAGS}

    -Werror                  # Make all warnings errors.
#    -Hretwc                  # Consider a particular warning to be an error, or all to be errors.
)
ENDIF()

# Add default global C flags.
ADD_C_FLAGS(
    ${COMPILE_FLAGS}         # Include all the common C/ASM flags.
)

# Indicate the compilation is done in the ROM repo.
IF(ROM_BUILD)
    ADD_DEFINITIONS(-DROM_BUILD)
ENDIF()

IF(NOT SDK_BUILD AND INLINE_CODE_IN_ASSEMBLY_DUMP)
    ADD_C_FLAGS(-Hkeepasm -fverbose-asm)
ENDIF()

# Add default global ASM flags.
ADD_ASM_FLAGS(
    ${COMPILE_FLAGS}         # Include all the common C/ASM flags.
    -Hasopt=-on=assume_short # Convert 32-bit instructions to 16-bit forms where possible.
)

# Add default global LINK flags.
ADD_LD_FLAGS(
    -Wl,-q                   # Don't display copyright message.
    -Wl,-Bgrouplib           # Search all archives together as a group.
    -Wl,-Xnocompress         # Never compress the .initdat section.
    -zallow_memory_overlap   # Allow the memory regions to overlap.
)

# Global device definitions.
ADD_DEFINITIONS(
    -DDEVICE=0x${TARGET_HW}
    -D__T${TARGET_HW}__
)

# Optionnal definitions.
IF(USE_SW_LOG2P1)
    ADD_DEFINITIONS(-DUSE_SW_LOG2P1=1)
ENDIF()
