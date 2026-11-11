"""
Week 8 EDUCATIONAL demo: public-key cryptography with a tiny "textbook RSA".

    python scripts/public_key_demo.py

!!! NOT SECURE – the numbers are tiny so humans can follow the maths.
!!! It is NOT used anywhere in the Study Planner. Passwords use Django's
!!! built-in hashing, and real HTTPS uses the web server's TLS software.
"""
from math import gcd

# 1. Pick two (small) primes.
p, q = 61, 53
n = p * q                      # 3233, part of both keys
phi = (p - 1) * (q - 1)        # 3120

# 2. Public exponent e (must share no factor with phi), private exponent d.
e = 17
assert gcd(e, phi) == 1
d = pow(e, -1, phi)            # modular inverse -> 2753

public_key, private_key = (e, n), (d, n)
print(f"Public key  (share with everyone): {public_key}")
print(f"Private key (keep secret)        : {private_key}")

# 3. Encryption: anyone can lock a message with the PUBLIC key...
message = 65                   # a number < n, e.g. the letter 'A'
ciphertext = pow(message, e, n)
print(f"\nMessage {message} -> encrypted with public key -> {ciphertext}")

# 4. ...but only the PRIVATE key holder can unlock it.
print(f"Ciphertext {ciphertext} -> decrypted with private key -> {pow(ciphertext, d, n)}")

# 5. Signatures work the other way round: sign with private, verify with public.
signature = pow(message, d, n)
print(f"\nSignature of {message} made with private key -> {signature}")
print(f"Verified with public key: {pow(signature, e, n) == message}")

print("\nIn HTTPS: the server's certificate holds its public key. Your browser uses it to")
print("agree on a fresh shared session key; the server proves identity with its private key.")
