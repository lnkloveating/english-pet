import argparse
import asyncio
import wave
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import websockets
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from shengsheng_agent.asr import (
    AsrAudioConfig,
    AsrProviderError,
    DoubaoStreamingAsrProvider,
    build_asr_provider,
)
from shengsheng_agent.config import Settings


async def pcm_chunks(path: Path) -> tuple[AsrAudioConfig, AsyncIterator[bytes]]:
    with wave.open(str(path), "rb") as source:
        config = AsrAudioConfig(
            sample_rate=source.getframerate(),
            bits=source.getsampwidth() * 8,
            channels=source.getnchannels(),
        )
    frames_per_chunk = max(1, config.sample_rate // 10)

    async def chunks() -> AsyncIterator[bytes]:
        with wave.open(str(path), "rb") as source:
            while chunk := source.readframes(frames_per_chunk):
                yield chunk
                await asyncio.sleep(0.1)

    return config, chunks()


async def run(path: Path) -> int:
    config, chunks = await pcm_chunks(path)
    if config.bits != 16 or config.channels != 1:
        print("Smoke test WAV must be 16-bit mono PCM")
        return 2

    provider = build_asr_provider(Settings())
    received = False
    try:
        async for event in provider.transcribe(chunks, audio=config, user_id="asr_smoke_test"):
            received = True
            kind = "final" if event.is_final else "partial"
            print(f"{kind}: {event.text}")
    except AsrProviderError as exc:
        print(f"ASR smoke test failed: {exc}")
        return 1
    return 0 if received else 2


async def check_handshake() -> int:
    provider = build_asr_provider(Settings())
    if not isinstance(provider, DoubaoStreamingAsrProvider):
        print("Set ASR_PROVIDER=doubao_streaming before running the handshake test")
        return 2
    connection_id = str(uuid4())
    async with websockets.connect(
        provider.websocket_url,
        additional_headers=provider._headers(connection_id),
        open_timeout=provider.timeout_seconds,
        close_timeout=5,
    ):
        print("Doubao ASR 2.0 handshake: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real Doubao streaming ASR smoke test")
    parser.add_argument("wav", nargs="?", type=Path, help="16-bit mono PCM WAV file")
    parser.add_argument("--handshake-only", action="store_true")
    args = parser.parse_args()
    if args.handshake_only:
        return asyncio.run(check_handshake())
    if args.wav is None:
        parser.error("wav is required unless --handshake-only is used")
    return asyncio.run(run(args.wav))


if __name__ == "__main__":
    raise SystemExit(main())
