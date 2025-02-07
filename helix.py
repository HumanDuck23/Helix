"""
Usage: helix.py <source>
"""

from enum import Enum
import sys


##########
# UTILS
##########

class CODON(Enum):
    # Program Control
    START = "ATG"
    STOP = "TGA"

    # Self-modification
    MUT = "CAG"
    DEL = "CTT"
    INS = "CTA"
    DUP = "CCA"
    TRP = "CCG"
    REV = "CCC"

    # Data and arithmetic
    LDI = "AAA"
    LD = "AAG"
    ST = "AAC"
    ADDI = "AAT"
    CMP = "ATA"
    SETF = "TAT"

    # I/O
    OUT = "GTA"
    IN = "GAT"


def is_valid_codon(codon: str) -> bool:
    """
    Check if the provided codon is valid or not.
    :param codon:
    :return: Validity of the codon
    """
    for char in codon.lower():
        if char not in ["a", "t", "c", "g"]:
            return False

    return len(codon) == 3


def codon_to_number(codon: str, signed: bool = False) -> int:
    """
    Interprets the passed codon as a signed or unsigned int and returns the result
    :param codon:
    :param signed:
    :return: Parsed int
    """
    if len(codon) != 3 or not is_valid_codon(codon):
        raise ValueError(
            f"Codon {codon} is improperly formatted! Codons must be 3 characters and only contain A, T, C, G.")

    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    value = (16 * mapping[codon[0]]) + (4 * mapping[codon[1]]) + mapping[codon[2]]
    if signed:
        return value if value < 32 else value - 64
    else:
        return value


def number_to_codon(number: int, signed: bool = False) -> str:
    """
    Converts a number to its codon counterpart
    :param number:
    :return:
    """
    if not signed:
        if not (0 <= number <= 63):
            raise ValueError(f"Number to be converted ({number}) is not in the allowed unsigned range!!! >:(")

        mapping = ['A', 'C', 'G', 'T']

        x = number // 16  # Most significant digit
        y = (number % 16) // 4  # Middle digit
        z = number % 4  # Least significant digit

        return mapping[x] + mapping[y] + mapping[z]
    else:
        if not (-32 <= number <= 31):
            raise ValueError(f"Number to be converted ({number}) is not in the allowed signed range!!! >:(")

        unsigned_value = number if number >= 0 else number + 64
        return number_to_codon(unsigned_value)


def process_into_strand(code: str) -> list[str]:
    """
    Takes the provided code and parses it into sets of codons to be fed to the interpreter.
    :param code:
    :return: A list of codons
    """
    if len(code) % 3 != 0:
        raise ValueError("Invalid codon formatting detected! Perhaps you are missing (or have too many) "
                         "nucleotides?")

    strand = []
    codon = ""
    for char in code:
        codon += char
        if len(codon) == 3:
            strand.append(codon)
            codon = ""

    return strand


def character_encode(char: str) -> int:
    """
    Encodes a character to its integer equivalent
    :param char:
    :return:
    """

    char_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 \n"
    try:
        return char_map.index(char)
    except ValueError:
        raise ValueError(f"Somehow the character ({char}) passed the filters but wasn't able to be converted. (*/ω＼*)")


def character_decode(char: int) -> str:
    char_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 \n"
    try:
        return char_map[char]
    except IndexError:
        raise ValueError(f"Somehow the character ({char}) passed the filters but wasn't able to be converted. (*/ω＼*)")


##########
# INTERPRETER
##########


class HelixInterpreter:
    def __init__(self):
        self.acc_register = ""
        self.flag_register = 0
        self.ip = 0

        self.executing = False
        self.strand = []

    def run(self, code):
        self.strand = process_into_strand(code)

        # Find the first ATG and start from there
        try:
            self.ip = self.strand.index(CODON.START.value) + 1
            self.executing = True
        except ValueError:
            raise ValueError("No START codon (ATG) found! I can't execute thin air.")

        while self.ip < len(self.strand):
            self.handle_codon()
            self.ip += 1

    def handle_codon(self):
        """
        Handles the codon at the current IP.
        :return:
        """
        current_codon = self.strand[self.ip]

        if not is_valid_codon(current_codon):
            print(f"Encountered an invalid codon: {current_codon}. Shutting down...")
            sys.exit(0)

        match current_codon:
            case CODON.STOP:
                print("Encountered a STOP codon. Halting execution...")
                sys.exit(1)

            case CODON.MUT:
                [orig, offset, new_codon] = self.get_codon_args(2)
                offset_number = codon_to_number(offset)
                try:
                    self.strand[orig + offset_number] = new_codon
                except IndexError:
                    raise ValueError("You tried mutating a codon that doesn't exist! Silly you...")

            case CODON.DEL:
                [orig, offset] = self.get_codon_args(1)
                offset_number = codon_to_number(offset)
                try:
                    del self.strand[orig + offset_number]
                except IndexError:
                    raise ValueError("You tried deleting a codon that doesn't exist! But why...?")

            case CODON.INS:
                [orig, offset, new_codon] = self.get_codon_args(2)
                offset_number = codon_to_number(offset)
                try:
                    self.strand.insert(orig + offset_number, new_codon)
                except IndexError:
                    raise ValueError(
                        "You tried inserting a codon to a place that doesn't exist. Who knows where it is now...")

            case CODON.DUP:
                [orig, start_offset, length] = self.get_codon_args(2)
                offset_number = codon_to_number(start_offset)
                length_number = codon_to_number(length)

                ins_codons = []
                try:
                    for i in range(length_number):
                        ins_codons.append(self.strand[orig + offset_number + i + 1])
                except IndexError:
                    raise ValueError("You tried inserting codons that don't exist. What am I supposed to do now?")

                try:
                    new_index = orig + offset_number + length_number
                    self.strand[new_index:new_index] = ins_codons
                except Exception:
                    raise ValueError("You tried inserting codons into somewhere nonexistent. Welp.")

            case CODON.TRP:
                [orig, source_offset, length, dest_offset] = self.get_codon_args(3)
                offset_number = codon_to_number(source_offset)
                length_number = codon_to_number(length)
                dest_offset_number = codon_to_number(dest_offset)

                cut_codons = []
                try:
                    for i in range(length_number):
                        cut_codons.append(self.strand[orig + offset_number + i + 1])
                except IndexError:
                    raise ValueError("You tried cutting codons that don't exist. What am I supposed to do now?")

                try:
                    self.strand[orig + dest_offset_number:orig + dest_offset_number] = cut_codons
                    del self.strand[orig + offset_number: orig + offset_number + length_number]
                except Exception:
                    raise ValueError(
                        "You tried moving the cut codons to somewhere out of this DNA strand. Quite a silly thing to "
                        "do, if you ask me...")

            case CODON.REV:
                [orig, start_offset, length] = self.get_codon_args(2)
                offset_number = codon_to_number(start_offset)
                length_number = codon_to_number(length)

                try:
                    self.strand[orig + offset_number:orig + offset_number + length] = list(
                        reversed(self.strand[orig + offset_number:orig + offset_number + length]))
                except Exception:
                    raise ValueError(
                        "You messed something up reversing. Maybe you drove into something. Check your offsets.")

            case CODON.LDI:
                [_, num] = self.get_codon_args(1)  # we don't always need the original IP from here on in
                self.acc_register = num  # we don't parse this yet as it will be interpreted based on context

            case CODON.LD:
                [orig, offset] = self.get_codon_args(1)
                offset_number = codon_to_number(offset, True)
                try:
                    self.acc_register = self.strand[orig + offset_number]
                except IndexError:
                    raise ValueError(
                        "You tried loading a codon that doesn't exist into the ACC register. Should I just make up a "
                        "number??")

            case CODON.ST:
                [orig, offset] = self.get_codon_args(1)
                offset_number = codon_to_number(offset, True)

                if self.acc_register == "":
                    raise ValueError("You tried storing the ACC register, but you never set it... Rookie mistake, smh.")

                try:
                    self.strand[orig + offset_number] = self.acc_register
                except IndexError:
                    raise ValueError("You tried storing the ACC register to a codon that doesn't exist. Huh.")

            case CODON.ADDI:
                [orig, num_codon] = self.get_codon_args(1)
                num = codon_to_number(num_codon, True)

                if self.acc_register == "":
                    raise ValueError("You tried adding to the ACC register without setting it. Yikes.")

                acc_num = codon_to_number(self.acc_register, True)
                acc_num += num
                self.acc_register = number_to_codon(acc_num, True)

            case CODON.CMP:
                [orig, comp] = self.get_codon_args(1)

                if self.acc_register == "":
                    raise ValueError("You tried comparing to the ACC register. Maybe you should set it first?")

                self.flag_register = 1 if self.acc_register == comp else 0

            case CODON.SETF:
                [orig, flag] = self.get_codon_args(1)

                if flag[0] in ["A", "C"]:
                    self.flag_register = 1
                else:
                    self.flag_register = 0

            case CODON.OUT:
                if self.acc_register == "":
                    raise ValueError("You tried outputting the ACC register. Since it's not set, I don't see what "
                                     "you're trying to accomplish. Silly goose.")

                print(character_decode(codon_to_number(self.acc_register)), end="")

            case CODON.IN:
                char_in = input()
                char_num = character_encode(char_in)
                self.acc_register = number_to_codon(char_num)

    def get_codon_args(self, arg_count: int) -> list:
        """
        Gets the next `arg_count` codons and puts them in a list for you to use.
        The first element of the list is the current IP before arguments are read.
        Also moves the IP for you!
        :param arg_count:
        :return: List [original_ip, arg1, arg2, ... argN]
        """
        try:
            args = [self.ip]

            for _ in range(arg_count):
                self.ip += 1
                args.append(self.strand[self.ip])

            return args
        except Exception:
            raise ValueError(
                "You didn't provide enough arguments for this opcode. Which opcode? I don't know. Figure it out, "
                "I guess.")
