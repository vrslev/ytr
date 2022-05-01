# ytr — Yandex.Translate prompt

This is a CLI for Yandex's translate service. At some point I got tired of opening the website, so I made a CLI.

https://user-images.githubusercontent.com/75225148/166159403-a018d890-f1c5-42df-bab3-1d57f991d573.mov

## Installation

```console
pipx install ytr
```

If you don't use [`pipx`](https://github.com/pypa/pipx/) yet, install with `pip`:

```console
pip install ytr
```

## Usage

Just run `ytr`.

By default it uses `en` and `ru` language hints. You can override this behaviour with `--hints` flag, for example, `ytr --hints en de`.

That's it: enjoy!
