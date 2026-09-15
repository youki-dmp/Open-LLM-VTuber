import requests
from loguru import logger
from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    def __init__(
        self,
        engine_url="http://127.0.0.1:50021",
        speaker_name="冥鳴ひまり",
        style_name="ノーマル",
        speed_scale=1.0,
    ):
        self.engine_url = engine_url.rstrip("/")
        self.speaker_name = speaker_name
        self.style_name = style_name
        self.speed_scale = speed_scale
        self.file_extension = "wav"

        self.style_id = self._resolve_style_id(speaker_name, style_name)

    def _resolve_style_id(self, speaker_name, style_name) -> int:
        resp = requests.get(f"{self.engine_url}/speakers", timeout=10)
        resp.raise_for_status()
        for speaker in resp.json():
            if speaker["name"] != speaker_name:
                continue
            for style in speaker["styles"]:
                if style["name"] == style_name:
                    return style["id"]
        raise ValueError(
            f"VOICEVOX speaker/style not found: {speaker_name}/{style_name}. "
            f"Check GET {self.engine_url}/speakers for available names."
        )

    def generate_audio(self, text, file_name_no_ext=None):
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)

        try:
            query_resp = requests.post(
                f"{self.engine_url}/audio_query",
                params={"text": text, "speaker": self.style_id},
                timeout=30,
            )
            query_resp.raise_for_status()
            query = query_resp.json()
            query["speedScale"] = self.speed_scale

            synth_resp = requests.post(
                f"{self.engine_url}/synthesis",
                params={"speaker": self.style_id},
                json=query,
                timeout=30,
            )
            synth_resp.raise_for_status()
        except Exception as e:
            logger.critical(f"\nError: VOICEVOX unable to generate audio: {e}")
            logger.critical(f"Is VOICEVOX ENGINE running at {self.engine_url}?")
            return None

        with open(file_name, "wb") as f:
            f.write(synth_resp.content)

        return file_name
