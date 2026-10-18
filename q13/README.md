# Question 13: Terminal Recording and Ciphertext Decoding (termlog)

## Overview
This directory contains the files and instructions for solving Question 13 of IIT Madras TDS Week 1 Assignment.

- **Student Email**: `23f2003826@ds.study.iitm.ac.in`
- **Tool**: `termlog` (authenticated terminal session recorder signed with Google OAuth)

## Transforms & Decoding Pipeline
The challenge string provided by the exam server had undergone three reversible transforms:
1. **ROT13**
2. **String Reversal**
3. **Hex Encoding**

To reverse and decode the code, the pipeline executed inside the recorded session was:
```bash
echo "$CIPHERTEXT" | xxd -r -p | rev | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

Decoded Code: `TL-KYU88H2T`

## Verification
The recording was verified using `termlog verify`:
```
termlog verification
  ok: true
  cast: q13/demo.cast
  receipt: q13/demo.cast.jwt
  user: 23f2003826@ds.study.iitm.ac.in
  receipt signature: valid
  cast hash: valid
  proof header: valid
  Google identity: valid
```

## Archive Contents
The submission archive `submission.tar.gz` contains:
- `demo.cast` (recorded terminal session)
- `demo.cast.jwt` (cryptographic signature proving user identity)

