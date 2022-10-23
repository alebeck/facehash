# facehash - verify data integrity with hyper-realistic human faces

![](teaser_dark.png#gh-dark-mode-only)
![](teaser_light.png#gh-light-mode-only)

## What is this?

Cryptographic hash functions are widely used for verifying data integrity, but hexadecimal (or worse, binary) representations are hard for humans to remember. In contrast, humans have evolved to parse other human faces instantly and to [store thousands of them in memory.](https://www.science.org/content/article/average-person-can-recognize-5000-faces#:~:text=To%20qualify%20as%20%22knowing%22%20a,of%20the%20Royal%20Society%20B%20.)

This makes faces the ideal representation for cryptographic hashes, at least for quickly checking if some data has changed, even after a long time has passed.

## Usage

You need a Linux environment with Python >=3.7 and PyTorch >=1.8 installed. Then install via:

```bash
pip install git+https://github.com/alebeck/facehash
```

`facehash` should have been added to your `PATH`, just call it like

```bash
facehash file
# or
echo -n "hello world!" | facehash
# you can also specify an output file (instead of displaying)
echo -n "hello world!" | facehash -o out.png
```

The first run can take a bit longer as the StyleGAN2 model has to be downloaded and relevant PyTorch extensions are built.

## How does it work?

We calculate an extended (512 byte) SHA hash by appending eight nonce values to the input and concatenating the respective SHA-512 hashes. Each byte is expected to be uniformly distributed within its value range, due to the chaotic nature of the hash. We use a Box-Muller transform to deterministically map the uniformly distributed bytes to a 512-dimensional Gaussian latent vector, which is expected by the Generator function of NVIDIA's [StyleGAN2-ADA model](https://github.com/NVlabs/stylegan2-ada-pytorch).
