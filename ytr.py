import uuid
from typing import Any, TypedDict

import click
import httpx
import rich
import rich.traceback
import typer
from rich.console import Console
from rich.panel import Panel


def _raise_for_status_hook(response: httpx.Response) -> None:
    response.raise_for_status()


def get_client(transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        base_url="https://translate.yandex.net/api/v1/tr.json",
        params={"ucid": str(uuid.uuid1()).replace("-", ""), "srv": "android"},
        headers={
            "Accept": "application/json",
            "User-Agent": "ru.yandex.translate/3.20.2024",
        },
        event_hooks={"response": [_raise_for_status_hook]},
        transport=transport,  # pyright: ignore[reportGeneralTypeIssues]
    )


LangPair = tuple[str, str]


def _get_detect_params(languages: LangPair, text: str) -> dict[str, Any]:
    return {"text": text, "hint": languages}


def _parse_detect_response(response: dict[str, Any]) -> str:
    assert response.get("code") == 200, f"`code` is not 200: {response}"
    assert response.get("lang"), f"`lang` not in response: {response}"
    return response["lang"]


def detect(client: httpx.Client, languages: LangPair, text: str) -> str:
    params = _get_detect_params(languages=languages, text=text)
    response = client.get(  # pyright: ignore[reportUnknownMemberType]
        "/detect", params=params
    ).json()
    return _parse_detect_response(response)


def _get_translate_params(from_: str, to: str) -> dict[str, str]:
    return {"lang": f"{from_}-{to}", "format": "text"}


def _get_translate_form_data(text: str) -> dict[str, str]:
    return {"text": text}


def _parse_translate_response(response: dict[str, Any]) -> str:
    assert response.get("code") == 200, f"`code` is not 200: {response}"
    assert response.get("text"), f"`text` not in response: {response}"
    return response["text"][0]


def translate(client: httpx.Client, from_: str, to: str, text: str) -> str:
    params = _get_translate_params(from_=from_, to=to)
    form = _get_translate_form_data(text=text)
    response = client.post(  # pyright: ignore[reportUnknownMemberType]
        "/translate", params=params, data=form
    ).json()
    return _parse_translate_response(response)


def _resolve_destination_lang(languages: LangPair, from_: str) -> str:
    if from_ not in languages:
        return languages[1]

    return languages[1] if languages[0] == from_ else languages[0]


class DetectAndTranslateResponse(TypedDict):
    from_: str
    to: str
    text: str
    translated: str


def detect_and_translate(
    client: httpx.Client, languages: LangPair, text: str
) -> DetectAndTranslateResponse:
    from_ = detect(client=client, languages=languages, text=text)
    to = _resolve_destination_lang(languages=languages, from_=from_)
    translated = translate(client=client, from_=from_, to=to, text=text)
    return {"from_": from_, "to": to, "text": text, "translated": translated}


def _run_once(languages: LangPair, client: httpx.Client, console: Console) -> None:
    console.print("[bold][bright_magenta]\n>[/bright_magenta][/bold]", end="")
    text = click.prompt("", type=str, prompt_suffix="")
    response = detect_and_translate(client=client, languages=languages, text=text)
    console.print(
        f"[italic][bright_blue]{response['from_']}[/bright_blue][/italic]",
        "->",
        f"[italic][bright_yellow]{response['to']}[/bright_yellow][/italic]",
    )
    console.print(Panel.fit(f"[bold][yellow]{response['translated']}[/yellow][/bold]"))


def _run(hints: LangPair = ("en", "ru")) -> None:
    client = get_client()
    console = rich.get_console()

    while True:
        _run_once(languages=hints, client=client, console=console)


def main() -> None:
    rich.traceback.install()
    typer.run(_run)


if __name__ == "__main__":
    main()
