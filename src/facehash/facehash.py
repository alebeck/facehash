import sys
import hashlib
import pickle
import math

import click
import torch
from PIL import Image

import dnnlib

EPS = 1e-8
MODELS_BASE_URL = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/'


def latent_from_bytes(hash_bytes: bytes) -> torch.Tensor:
    """
    Translates uniformly distributed bytes into an (approximately) Gaussian latent vector of equal size,
    using the Box-Muller transform (https://en.wikipedia.org/wiki/Box–Muller_transform)
    """
    rep = torch.tensor(list(hash_bytes)).float()
    # map into (0, 1) interval
    rep /= 255.

    # time for Box-Muller
    rep = rep.clip(EPS)
    a = torch.sqrt(-2. * torch.log(rep[::2]))
    b = 2. * math.pi * rep[1::2]
    z1 = a * torch.cos(b)
    z2 = a * torch.sin(b)

    # this is our latent generator representation
    return torch.cat([z1, z2])


def generate_image(G: torch.nn.Module, z: torch.Tensor) -> Image:
    img = G(z.unsqueeze(0).cuda(), None)
    img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    img = Image.fromarray(img[0].cpu().numpy(), 'RGB')
    return img


@click.command()
@click.argument('filename', required=False)
@click.option('-m', '--model', default='ffhq', type=click.Choice(['ffhq']),  help='Generative model to use')
@click.option('-o', '--out', 'save_filename', help='Save hash image to file')
@click.option('-s', '--resize', default=256, help='Resize square output image to N pixels')
def main(filename, model, save_filename, resize):
    if filename is not None:
        with open(filename, 'rb') as fh:
            in_bytes = fh.read()
    else:
        # read from stdin
        in_bytes = bytes(sys.stdin.read(), 'UTF-8')

    # extend hash to 512 bytes by prepending 8 different nonce values
    hash_bytes = b''
    for nonce in range(8):
        hash_bytes += hashlib.sha512(nonce.to_bytes(1, 'big') + in_bytes).digest()

    z = latent_from_bytes(hash_bytes)

    with dnnlib.util.open_url(MODELS_BASE_URL + f'{model}.pkl') as f:
        G = pickle.load(f)['G_ema'].cuda()

    img = generate_image(G, z)

    if resize is not None:
        img = img.resize((resize, resize))

    if save_filename is not None:
        img.save(save_filename)
    else:
        # display using GTK
        img.show()


if __name__ == '__main__':
    main()
