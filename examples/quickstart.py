        """Minimal MuseTalk example: create one prediction and print the output URL(s)."""
        import musetalk_api

        output = musetalk_api.run({
    "image_url": "https://example.com/input.png",
    "audio_url": "https://example.com/input.png"
})
        print(output)
