# Helix Documentation

Helix is an esoteric, self–modifying, Turing–complete programming language inspired by biological DNA. In this language,
**all instructions and data are encoded as codons**—triplets of nucleotides (A, T, C, G). The language eschews explicit
jump or branch instructions; instead, all control flow is achieved by unconditionally executing self–modification
operations on the program’s own DNA.

---

## Table of Contents

- [Architectural Overview](#architectural-overview)
- [Numeric Conventions](#numeric-conventions)
- [Instruction Set](#instruction-set)
    - [Program Control Instructions](#program-control-instructions)
    - [Self–Modification Instructions](#self-modification-instructions)
    - [Data and Arithmetic Instructions](#data-and-arithmetic-instructions)
- [Notes on Control Flow](#notes-on-control-flow)

---

## Architectural Overview

- **Unified DNA Memory:**  
  The entire program—code and data alike—is stored in a single mutable DNA strand. Every instruction is a codon.

- **Sequential Execution:**  
  A dedicated polymerase (the instruction pointer, or IP) reads the DNA one codon at a time from left to right. There
  are no built-in jump or branch instructions; instead, self–modification rewrites the DNA to alter the control flow.

- **Registers:**
    - **ACC (Accumulator):** A single working register that holds one codon (interpreted as a 6–bit number).
    - **FLAG:** A Boolean register set by comparison operations. Although FLAG is not used for conditional execution
      directly, its numeric value (1 for TRUE, 0 for FALSE) is employed in arithmetic computations to influence
      self–modification.

---

## Numeric Conventions

- **Mapping:**
    - A = 0
    - C = 1
    - G = 2
    - T = 3

- **Codon-to-Number Conversion:**  
  A codon _XYZ_ represents the number:

  $value = 16 × digit(X) + 4 × digit(Y) + digit(Z)$

This gives a value in the range 0–63.

- **Signed Numbers (Two’s Complement):**  
  If the computed value is ≥ 32, subtract 64 to obtain a signed integer (range –32 to 31). *Note*: Stored numbers are
  not always interpreted as signed. Please refer to the documentation of the desired instruction to see what it does.

---

## Instruction Set

All instructions are represented by a codon opcode, possibly followed by one or more parameter codons. All addressing is
**relative to the current IP** (that means the **instruction** codon, not the parameter giving the offset).

### Program Control Instructions

| **Opcode** | **Codon** | **Mnemonic** | **Parameters** | **Effect**                                                                                |
|------------|-----------|--------------|----------------|-------------------------------------------------------------------------------------------|
| START      | `ATG`     | START        | 0              | Marks the beginning of execution. The IP starts at the codon immediately following `ATG`. |
| STOP       | `TGA`     | STOP         | 0              | Halts execution.                                                                          |

---

### Self–Modification Instructions

These instructions rewrite the DNA and are the only means to alter the natural sequential flow. The `offset` parameter
of *all* these instructions is read as *unsigned*, as modifying already executed code is silly.

| **Opcode** | **Codon** | **Parameters**                                | **Effect**                                                                                                                                |
|------------|-----------|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| MUT        | `CAG`     | 2 (offset, new codon)                         | Replaces the codon at `(IP + offset)` with the supplied new codon.                                                                        |
| DEL        | `CTT`     | 1 (offset)                                    | Deletes the codon at `(IP + offset)`.                                                                                                     |
| INS        | `CTA`     | 2 (offset, codon to insert)                   | Inserts the given codon at `(IP + offset)`, shifting subsequent codons right.                                                             |
| DUP        | `CCA`     | 2 (start offset, length)                      | Duplicates a block of codons starting at `(IP + start offset)` (spanning the given length) and inserts it immediately after the original. |
| TRP        | `CCG`     | 3 (source offset, length, destination offset) | Cuts a block of codons (of the given length) starting at `(IP + source offset)` and inserts it at `(IP + destination offset)`.            |
| REV        | `CCC`     | 2 (start offset, length)                      | Reverses the order of codons in the block starting at `(IP + start offset)` over the specified length.                                    |

---

### Data and Arithmetic Instructions

These instructions operate on the ACC and FLAG, setting up data for later use in self–modification. Here, **offset**
arguments are interpreted as **signed**.

| **Opcode** | **Codon** | **Parameters**      | **Effect**                                                                                           |
|------------|-----------|---------------------|------------------------------------------------------------------------------------------------------|
| LDI        | `AAA`     | 1 (immediate codon) | Loads the immediate codon into ACC.                                                                  |
| LDF        | `AGT`     | 0                   | Loads FLAG into ACC.                                                                                 |
| LD         | `AAG`     | 1 (offset)          | Loads the codon at `(IP + offset)` into ACC.                                                         |
| ST         | `AAC`     | 1 (offset)          | Stores the current ACC value into the DNA at `(IP + offset)`.                                        |
| ADDI       | `AAT`     | 1 (immediate codon) | Adds the immediate codon’s numeric value (interpreted as signed) to ACC (modulo 64).                 |
| CMP        | `ATA`     | 1 (immediate codon) | Compares ACC with the immediate value. Sets FLAG to TRUE if equal, otherwise FALSE.                  |
| SETF       | `TAT`     | 1 (flag codon)      | Sets FLAG based on the parameter codon (interpreting the first nucleotide: A/C = TRUE, G/T = FALSE). |

---

### I/O Instructions

Helix also provides simple input and output instructions for interacting with external data.

| **Opcode** | **Codon** | **Parameters** | **Effect**                                                                                               |
|------------|-----------|----------------|----------------------------------------------------------------------------------------------------------|
| OUT        | `GTA`     | 0              | Outputs the current value in ACC to the output stream as a character per the encoding below.             |
| IN         | `GAT`     | 0              | Reads a 6–bit input value from the input stream and stores it in ACC (again, as per the encoding below). |

---

## Character Encoding

When reading data stored in codons as characters, they are interpreted as unsigned integers. This results in the numbers
0-63 being available to you. The character encoding in Helix is designed as follows:

- **Alphabetic Characters:**
  Alphabetic characters are mapped to their corresponding numerical value. This starts at *A = 0* ... *Z = 25*, *a =
  26* ... *z = 51*.

- **Digits:**
  Digits are encoded from *0 = 52* ... *9 = 61*.

- **Additional Characters:**
  The remaining two character codes, *62* and *63*, correspond to *space* and *newline*, respectively.

---

## Notes on Control Flow

- **Unconditional Execution:**  
  Every instruction in Helix is executed sequentially. There is no built-in mechanism for conditional execution or
  jumps.

- **Self–Modification for Flow Control:**  
  All loops, conditionals, and other control structures must be implemented by rewriting the DNA (using instructions
  such as MUT, DEL, INS, DUP, TRP, and REV).

- **Data–Driven Decisions:**  
  While FLAG holds a Boolean (TRUE/FALSE), you can use arithmetic (by treating TRUE as 1 and FALSE as 0) to compute
  offsets or candidate values. This computed value then guides which data or code is used later—thus simulating
  conditional behavior without explicit branch instructions.

---

*Good luck!*
