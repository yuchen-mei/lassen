from dataclasses import dataclass
from peak.bits import Bits
from peak.enum import Enum
from peak.product import Product
from .cond import Cond
from .mode import Mode
from .lut import Bit, LUT

# https://github.com/StanfordAHA/CGRAGenerator/wiki/PE-Spec

# Current PE has 16-bit data path
DATAWIDTH = 16
Data = Bits(DATAWIDTH)

# MANT=8
# EXP=8
# FloatData = Bits(MANT-1+EXP+1)

# Constant values for registers
RegA_Const = Bits(DATAWIDTH)
RegB_Const = Bits(DATAWIDTH)
RegD_Const = Bits(1)
RegE_Const = Bits(1)
RegF_Const = Bits(1)

# Modes for registers
RegA_Mode = Mode
RegB_Mode = Mode
RegD_Mode = Mode
RegE_Mode = Mode
RegF_Mode = Mode

# ALU operations
class ALU(Enum):
    Add          = 0x0
    Sub          = 0x1
    Abs          = 0x3
    GTE_Max      = 0x4
    LTE_Min      = 0x5
    Sel          = 0x8
    Mult0        = 0xb
    Mult1        = 0xc
    Mult2        = 0xd
    SHR          = 0xf
    SHL          = 0x11
    Or           = 0x12
    And          = 0x13
    XOr          = 0x14
    FAdd         = 0x90
    FMul         = 0x91
    FGetMant     = 0x92
    FAddIExp     = 0x93
    FSubExp      = 0x94
    FCnvExp2F    = 0x95
    FGetFInt     = 0x96
    FGetFFrac    = 0x97
# Whether the operation is unsigned (0) or signed (1)
Signed = Bits(1)

#
# Each configuration is given by the following fields
#
@dataclass
class Inst(Product):
    alu:ALU          # ALU operation
    signed:Signed    # unsigned or signed 
    lut:LUT          # LUT operation as a 3-bit LUT
    cond:Cond        # Condition code (see cond.py)
    rega:RegA_Mode   # RegA mode (see mode.py)
    data0:RegA_Const # RegA constant (16-bits)
    regb:RegB_Mode   # RegB mode
    data1:RegB_Const # RegB constant (16-bits)
    regd:RegD_Mode   # RegD mode
    bit0:RegD_Const  # RegD constant (1-bit)
    rege:RegE_Mode   # RegE mode
    bit1:RegE_Const  # RegE constant (1-bit)
    regf:RegF_Mode   # RegF mode
    bit2:RegF_Const  # RegF constant (1-bit)

