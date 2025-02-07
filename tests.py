import helix

print(helix.is_valid_codon("ATC"))
print(helix.is_valid_codon("TAG"))
print(helix.is_valid_codon("ATG"))
print(helix.is_valid_codon("GAT"))
print(helix.is_valid_codon("GFT"))
print(helix.is_valid_codon("ATCC"))
print(helix.is_valid_codon("AT"))
print("-=-=-=-=-=-=-=-=-=-=-")
nums = [-3, 20, 10, -11, 54, 63, 64, -33]
for num in nums:
    signed = num < 0
    codon = helix.number_to_codon(num, signed)
    print(f"{num} -> {codon}")
    nnum = helix.codon_to_number(codon, signed)
    print(f"{codon} -> {nnum}")

print("-=-=-=-=-=-=-=-=-=-=-")

print(helix.character_encode("A"))
print(helix.character_encode("Z"))
print(helix.character_encode("a"))
print(helix.character_encode("z"))
print(helix.character_encode("0"))
print(helix.character_encode("9"))
print(helix.character_encode(" "))
print(helix.character_encode("\n"))

print(helix.character_decode(helix.character_encode("A")))
print(helix.character_decode(helix.character_encode("Z")))
print(helix.character_decode(helix.character_encode("a")))
print(helix.character_decode(helix.character_encode("z")))
print(helix.character_decode(helix.character_encode("0")))
print(helix.character_decode(helix.character_encode("9")))
print(helix.character_decode(helix.character_encode(" ")))
print(helix.character_decode(helix.character_encode("\n")))
print("-=-=-=-=-=-=-=-=-=-=-")
