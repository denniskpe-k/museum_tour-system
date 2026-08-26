# Media Guide — Adding Real Photos, Video, and Audio

This app now has a **Media** button on every stop. Tap it and a
closeable window opens with three tabs — **Photos**, **Video**,
**Audio** — showing whatever real files exist for that stop. Nothing
about file paths or folders is ever shown to a visitor; if a file
hasn't been added yet, that tab just shows a friendly "not added yet"
message instead of breaking.

This guide tells you exactly which files to find, what to name them,
and where to put them so they show up automatically — you don't need
to touch any code.

## How it works (read this first)

Every filename below is already wired into the app in
`services/demo_data.py`. The app checks each folder at startup:

- If a file **exists** at the expected path → it plays/shows in the
  Media popup.
- If a file is **missing** → that tab shows "hasn't been added yet."

So you can add these gradually, one stop at a time, re-running the
app after each one to check it worked. Nothing will crash either way.

## The three folders

| Media type | Folder                     | Format(s)              |
|------------|-----------------------------|-------------------------|
| Photos     | `assets/images/`            | `.jpg` or `.png`        |
| Video      | `assets/video/`              | `.mp4` (H.264 video)    |
| Audio      | `assets/audio/`               | `.mp3` or `.wav`         |

Just drop a file in with the **exact filename** listed below — no
renaming needed on the app's side, no code changes.

## Where to find real, freely-usable media

Use sources that offer content free for reuse (check the license on
each file before downloading):

- **Photos**: [Wikimedia Commons](https://commons.wikimedia.org),
  [Unsplash](https://unsplash.com), [Pexels](https://pexels.com),
  [Pixabay](https://pixabay.com), or museum open-access collections
  (e.g. The Met, Rijksmuseum, Smithsonian all have public-domain
  photo archives).
- **Video**: [Pexels Videos](https://pexels.com/videos),
  [Pixabay Video](https://pixabay.com/videos),
  [Coverr](https://coverr.co) — search for the room/artifact theme
  (e.g. "museum gallery," "sculpture garden," "ancient pottery").
  Keep clips short (10–30 seconds is plenty for a tour stop).
- **Audio (narration/ambience)**: record your own narration on a
  phone (free), or use [Freesound](https://freesound.org) for
  ambient museum/room sound. For real spoken narration, the project
  already includes an offline text-to-speech generator
  (`services/audio_generator.py`) if you'd rather generate it than
  record it.

If a file is a video, convert it to `.mp4`/H.264 first if it isn't
already — most free download sites already offer this format.

## Checklist by stop

Files marked **✅ already included** came with the project and don't
need to be sourced. Everything else is a placeholder filename —
find or create a file, save it with that exact name, and drop it in
the matching folder.

### Tour 1 — Highlights of Modern Art

**Entrance Hall**
- Photo: `assets/images/entrance_hall_1.jpg` — the museum's entrance hall
- Video: `assets/video/entrance_hall.mp4` — a short establishing shot of the entrance
- Audio: `assets/audio/welcome.wav` — ✅ already included (generated narration)

**Cubism Room**
- Photo: `assets/images/cubism_artwork.jpg` — ✅ already included
- Photo: `assets/images/cubism_room_2.jpg` — a wider shot of the gallery room
- Video: `assets/video/cubism_room.mp4` — a walkthrough or close-up pan of Cubist works
- Audio: `assets/audio/cubism_room.mp3` — narration or ambient gallery sound

**Sculpture Garden**
- Photo: `assets/images/sculpture_garden_1.jpg` — a stone sculpture
- Photo: `assets/images/sculpture_garden_2.jpg` — a welded-steel sculpture
- Video: `assets/video/sculpture_garden.mp4` — an outdoor garden walkthrough
- Audio: `assets/audio/sculpture_garden.mp3` — narration or outdoor ambience

**Contemporary Wing**
- Photo: `assets/images/contemporary_wing_1.jpg` — a contemporary art piece
- Video: `assets/video/contemporary_wing.mp4` — a short room walkthrough
- Audio: `assets/audio/voices_of_now.wav` — ✅ already included (generated narration)

### Tour 2 — Treasures Through Time

**The Heart of the Ocean**
- Photo: `assets/images/heart_of_ocean_necklace.jpg` — ✅ already included
- Photo: `assets/images/heart_of_ocean_2.jpg` — a close-up detail shot
- Video: `assets/video/heart_of_ocean.mp4`
- Audio: `assets/audio/heart_of_ocean.mp3`

**Victorian Jewel Case**
- Photo: `assets/images/heart_pendant_necklace.jpg` — ✅ already included
- Photo: `assets/images/victorian_jewel_case_2.jpg` — the display case itself
- Video: `assets/video/victorian_jewel_case.mp4`
- Audio: `assets/audio/victorian_jewel_case.mp3`

**Ancient Greece Gallery**
- Photo: `assets/images/greek_hydria_vase.jpg` — ✅ already included
- Photo: `assets/images/greek_gallery_2.jpg` — the gallery room
- Video: `assets/video/ancient_greece_gallery.mp4`
- Audio: `assets/audio/ancient_greece_gallery.mp3`

**Egyptian Wing**
- Photo: `assets/images/nefertiti_bust.jpg` — ✅ already included
- Photo: `assets/images/egyptian_wing_2.jpg` — the wing/gallery room
- Video: `assets/video/egyptian_wing.mp4`
- Audio: `assets/audio/egyptian_wing.mp3`

**Titanic Memorial Room**
- Photo: `assets/images/titanic_life_jacket.jpg` — ✅ already included
- Photo: `assets/images/titanic_memorial_room_2.jpg` — the memorial room
- Video: `assets/video/titanic_memorial_room.mp4`
- Audio: `assets/audio/titanic_memorial_room.mp3`

**Digital Restoration Lab**
- Photo: `assets/images/digital_restoration_lab_1.jpg` — inside the lab
- Video: `assets/video/digital_restoration_lab.mp4`
- Audio: `assets/audio/digital_restoration_lab.mp3`

## Adding more photos to a stop

Each stop can hold as many photos as you like — not just the two
listed above. Open `services/demo_data.py`, find the stop's
`"media"` block, and add another entry to its `"images"` list:

```python
"media": {
    "images": [
        {"path": "assets/images/cubism_artwork.jpg", "caption": "A Cubist painting on display"},
        {"path": "assets/images/cubism_room_2.jpg", "caption": "The Cubism Room gallery space"},
        {"path": "assets/images/cubism_room_3.jpg", "caption": "Your new caption here"},  # add this
    ],
    ...
},
```

Then drop the matching file into `assets/images/`. The Photos tab
automatically picks up any extra entries and lets visitors flip
through them with Prev/Next.

## A note on video playback

The Video tab uses Kivy's built-in video player, which needs an
optional codec backend (`ffpyplayer` or `gstreamer`) installed on
the machine running the app. If neither is installed, real `.mp4`
files won't play — install one with:

```bash
pip install ffpyplayer
```

If no video backend is available at all, stops that also have the
older generated frame-animation (the Cubism Room's demo "video") will
still show that as a fallback preview; everything else will show the
"not added yet" message until a backend is installed.
