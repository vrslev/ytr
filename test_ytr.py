from typing import Any

import httpx
import pytest

from ytr import (
    _get_detect_params,
    _get_translate_form_data,
    _get_translate_params,
    _parse_detect_response,
    _parse_translate_response,
    _resolve_destination_lang,
    detect,
    detect_and_translate,
    get_client,
    translate,
)


def test_get_detect_params():
    assert _get_detect_params(("en", "ru"), "hello") == {
        "text": "hello",
        "hint": ("en", "ru"),
    }


def test_parse_detect_response_passes():
    assert _parse_detect_response({"code": 200, "lang": "en"}) == "en"


@pytest.mark.parametrize(
    "v", [{"code": 405}, {"code": 200}, {"code": 200, "lang": None}]
)
def test_parse_detect_response_fails(v: Any):
    with pytest.raises(AssertionError):
        _parse_detect_response(v)


def test_detect_ok():
    def handler(request: httpx.Request):
        assert request.url.params["text"] == "hello"
        assert request.url.params.get_list("hint") == ["en", "ru"]
        return httpx.Response(status_code=200, json={"code": 200, "lang": "ru"})

    client = get_client(httpx.MockTransport(handler))
    assert detect(client=client, languages=("en", "ru"), text="hello") == "ru"


def test_detect_fails():
    def handler(request: httpx.Request):
        return httpx.Response(status_code=400)

    client = get_client(httpx.MockTransport(handler))

    with pytest.raises(httpx.HTTPStatusError):
        detect(client=client, languages=("", ""), text="")


def test_get_translate_params():
    assert _get_translate_params("en", "ru") == {"lang": "en-ru", "format": "text"}


def test_get_translate_form_data():
    assert _get_translate_form_data("hello") == {"text": "hello"}


@pytest.mark.parametrize(
    "v",
    [
        {"code": 200, "text": ["hello", "world"]},
        {"code": 200, "lang": "en", "text": ["hello", "world"]},
    ],
)
def test_parse_translate_response_passes(v: Any):
    assert _parse_translate_response(v) == "hello"


@pytest.mark.parametrize(
    "v", [{"code": 402}, {"code": 200}, {"code": 200, "text": None}]
)
def test_parse_translate_response_fails(v: Any):
    with pytest.raises(AssertionError):
        _parse_translate_response(v)


def test_translate():
    def handler(request: httpx.Request):
        assert request.content.decode() == "text=hello"
        assert request.url.params["lang"] == "ru-en"
        assert request.url.params["format"] == "text"
        return httpx.Response(status_code=200, json={"code": 200, "text": ["hello"]})

    client = get_client(httpx.MockTransport(handler))
    assert translate(client=client, from_="ru", to="en", text="hello") == "hello"


@pytest.mark.parametrize(
    ["from_", "to"], [["en", "ru"], ["ru", "en"], ["whaaat", "ru"]]
)
def test_resolve_destination_lang(from_: str, to: str):
    assert _resolve_destination_lang(("en", "ru"), from_) == to


def test_detect_and_translate():
    def handler(request: httpx.Request):
        if "/detect" in request.url.path:
            return httpx.Response(status_code=200, json={"code": 200, "lang": "en"})
        else:
            assert request.content.decode() == "text=hello"
            assert request.url.params["lang"] == "en-ru"

            return httpx.Response(
                status_code=200, json={"code": 200, "text": ["здравствуйте"]}
            )

    client = get_client(httpx.MockTransport(handler))
    assert detect_and_translate(client=client, languages=("ru", "en"), text="hello")
