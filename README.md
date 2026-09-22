# MuseTalk API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=musetalk-dev&utm_content=readme-badge&utm_term=tier-a)

MuseTalk is Tencent Music's real-time lip synchronisation model: it inpaints the lower half of a face in a VAE latent space so the mouth matches any audio track, fast enough for live use. This package is a MuseTalk-class lip sync API client for Python: one `pip install` gives you audio-driven talking-head video as an HTTPS call, with no VAE, Whisper or U-Net checkpoints to download and no GPU to provision.

You get a blocking `run()` that returns the video URL, a submit-and-poll path for batches, webhook delivery on completion, and one runtime dependency (`httpx`). It is built for dubbing, e-learning and marketing pipelines that need a speaking face from a portrait and an audio file without owning inference hardware.

> **Try it now:** [https://synexa.ai/explore/veed/fabric-1.0](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=musetalk-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About MuseTalk](#about-musetalk)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No GPU to provision.** MuseTalk's real-time claim (30 fps and above) is measured on an NVIDIA V100; on smaller cards it drops well below that, and the preprocessing (face parsing, landmark detection) adds its own dependencies. The hosted endpoint runs on managed GPUs.
- **No environment to maintain.** No PyTorch/CUDA matching, no ffmpeg, mmpose or face-parsing installs, no checkpoint mirrors. Install, set a key, call `run()`.
- **No cold starts on your side.** Even a fast model has to be loaded and kept warm to be fast; that idle time is your bill when you self-host. Here you pay per prediction only.
- **Known price per clip.** `veed/fabric-1.0` is $0.08 per run, billed per prediction with no idle GPU charge.

## Installation

```bash
pip install git+https://github.com/musetalk-dev/musetalk-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=musetalk-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import musetalk_api

output = musetalk_api.run({
    "image_url": "https://example.com/input.png",
    "audio_url": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from musetalk_api import Client

client = Client(api_key="sk-...")
output = client.run({"image_url": "https://example.com/input.png", "audio_url": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`veed/fabric-1.0`](https://synexa.ai/explore/veed/fabric-1.0?utm_source=github&utm_medium=ugc&utm_campaign=musetalk-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Fabric 1.0 turns a photo plus an audio track into a talking-head video. | $0.08 |

The default model is **`veed/fabric-1.0`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `veed/fabric-1.0`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Portrait to animate (.jpg/.png/.webp). One clear, forward-facing face works best |
| `audio_url` | file | yes | — | — | Speech for the portrait to lip-sync to (.mp3/.wav/.flac/.m4a/.ogg) |
| `resolution` | string | no | `720p` | 720p, 480p | Output resolution of the talking-head video |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from musetalk_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About MuseTalk

MuseTalk is described in *MuseTalk: Real-Time High Quality Lip Synchronization with Latent Space Inpainting* from the Lyra Lab at Tencent Music Entertainment, released in 2024 alongside the MuseV and MusePose projects, with a 1.5 version in 2025. Its distinguishing property is speed: it is a single-pass model rather than an iterative diffusion sampler, which is why it can approach real-time frame rates.

The method masks the lower half of each face frame, encodes it with the `ft-mse-vae` from Stable Diffusion, and uses a U-Net (the same architecture family as Stable Diffusion's, but run once) to inpaint the mouth region conditioned on audio features from Whisper-tiny. Audio and visual features are fused with cross-attention. The 1.5 release added a two-stage training scheme with perceptual, GAN and sync losses and a spatio-temporal sampling strategy, improving clarity and lip-audio alignment.

Inputs are an existing video (or a single image) and an audio file; the output is the video with the mouth re-synchronised, with the face region processed at 256×256 and pasted back. Limits: the modified region is low resolution, so close-ups show softness; it re-dubs rather than generates head motion; and multiple or heavily rotated faces are not handled well.

The hosted endpoint used by this client is `veed/fabric-1.0`, which provides the same lip sync capability; it takes a portrait image plus an audio file and returns a talking-head video, so it animates a still photo rather than re-dubbing an existing clip. The original MuseTalk weights are available at https://github.com/TMElyralab/MuseTalk if you want to self-host.

**Official project:** https://github.com/TMElyralab/MuseTalk

## Use cases

- **Dub a presenter into new languages** — call `run({"image_url": portrait, "audio_url": translated_speech})` once per language and ship one video per market.
- **Course narration** — pair an instructor headshot with recorded lesson audio to produce a talking head for each module.
- **Personalised video messages** — generate a short clip per recipient from a TTS track, batched with `wait=False` and collected by webhook.
- **Podcast to video** — turn a host photo plus an episode segment into a speaking clip for social previews.
- **Product explainers** — regenerate the presenter for each locale while keeping the same screen recording.
- **Prototype a live avatar** — test the output quality of hosted lip sync before investing in a self-hosted real-time MuseTalk deployment.

## FAQ

**Is there a MuseTalk API?**

Not from Tencent; MuseTalk is released as open weights. This client exposes the same lip sync capability through a hosted talking-head endpoint (`veed/fabric-1.0`) that you call over HTTPS.

**How much does the MuseTalk API cost?**

The hosted `veed/fabric-1.0` model is $0.08 per run. Billing is per prediction; there is no hourly GPU charge.

**Can I run MuseTalk without a GPU?**

With this client, yes: generation happens on the hosted service and your code only makes HTTP requests. Self-hosting MuseTalk needs a CUDA GPU; its real-time figures assume a V100-class card.

**Does this client work with the original MuseTalk repo or ComfyUI?**

No. It does not load the TMElyralab/MuseTalk checkpoints and it is not a ComfyUI node. It is a network client for the hosted endpoint. If you need MuseTalk's real-time video-to-video path, run the official repository locally.

**What input formats does it accept?**

`image_url` (a portrait in .jpg/.png/.webp with one clear, forward-facing face) and `audio_url` (.mp3/.wav/.flac/.m4a/.ogg), plus an optional `resolution`. The output is a video URL. Video input is not accepted by the hosted endpoint.

**Is this the official MuseTalk SDK?**

No. This is an independent, community-maintained client and is not affiliated with Tencent Music Entertainment or VEED. The official project lives at https://github.com/TMElyralab/MuseTalk.

## Related

- [MuseTalk (official repository)](https://github.com/TMElyralab/MuseTalk) — paper, weights and real-time inference code.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client this package wraps.
- [veed/fabric-1.0](https://synexa.ai/explore/veed/fabric-1.0) — the hosted portrait-plus-audio talking-head model behind this client.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of MuseTalk. Model weights and trademarks belong to their respective owners.

_Last reviewed: 2026-09-22_
