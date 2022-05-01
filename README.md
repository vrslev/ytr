# ytr — Yandex.Translate prompt

This is a CLI for Yandex's translate service. At some point I got tired of opening the website, so I made a CLI.

https://user-images.githubusercontent.com/75225148/166160552-1e8846db-c52f-41ba-80e4-b5d28d4a5c79.mov

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
