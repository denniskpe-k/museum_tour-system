# APK Build Guide

This project can be packaged into a real Android `.apk` you can install
on a phone. The APK is **built in the cloud** by GitHub's free build
servers — you don't need Android Studio, the Android SDK/NDK, or even a
Linux machine on your own computer. This only works on GitHub (not
locally on Windows), because the underlying tool (Buildozer) doesn't
run on Windows at all, and downloading the Android SDK/NDK is a
multi-gigabyte, hour-plus process better left to a disposable cloud
runner than your laptop.

## What you need

- A free [GitHub](https://github.com) account.
- That's it. Everything else (Java, the Android SDK/NDK, Buildozer,
  Cython) is installed automatically by the workflow.

## Step 1 — Create a GitHub repository

1. Go to [github.com/new](https://github.com/new).
2. Name it anything, e.g. `museum-tour-system`.
3. Keep it **Public** (GitHub Actions free minutes are more generous for
   public repos) or Private — either works, just slower on Private.
4. Don't add a README/gitignore/license here — you already have those.
5. Click **Create repository**.

## Step 2 — Push this project to it

Open a terminal in your `museum_tour_system` folder and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

(Replace `<your-username>` and `<your-repo-name>` with your actual
GitHub username and the repo name you picked.)

## Step 3 — Watch it build

Pushing to `main` automatically triggers the build. On GitHub:

1. Open your repository in a browser.
2. Click the **Actions** tab at the top.
3. You'll see a run called **"Build Android APK"** — click it.
4. It takes **20–45 minutes** the first time (it's downloading and
   compiling the entire Android toolchain from scratch). Later runs are
   faster because the workflow caches most of that.

If you don't want to wait for a push, you can also trigger it manually:
Actions tab → "Build Android APK" (left sidebar) → **Run workflow**
button → **Run workflow**.

## Step 4 — Download the APK

Once the run finishes with a green checkmark:

1. Click into that run.
2. Scroll to the bottom — there's an **Artifacts** section.
3. Click **museum-tour-apk** to download a zip containing your `.apk`
   file.

## Step 5 — Install it on your phone

1. Transfer the `.apk` file to your Android phone (email it to
   yourself, use a USB cable, Google Drive, WhatsApp — anything).
2. Tap the file on your phone to install it.
3. Android will likely warn about "installing from unknown sources" the
   first time — this is normal for any app not from the Play Store.
   Tap **Settings** in that prompt and allow installs from whichever
   app you used to open the file (e.g. Files, Chrome, Gmail).
4. Tap install, then open the app.

## What works on the APK vs. desktop

Everything works the same as on your laptop **except**:

| Feature | On the APK |
|---|---|
| Tour selection, maps, quizzes, badges, offline storage | Identical |
| Real audio narration | Identical (files are bundled in the APK) |
| Generated "video" (frame animation) | Identical |
| Interactive 3D vase viewer | Identical — actually nicer, since dragging with a finger feels more natural than a mouse |
| Real webcam photo capture | Falls back to the simulated placeholder photo (OpenCV was deliberately left out of the Android build — see below) |
| Real .mp4 video playback | Not included in this build (ffpyplayer was left out — see below) |
| Native email sharing | Works if plyer installs correctly; otherwise falls back to the same clipboard/mailto behavior as desktop |

## Why OpenCV and ffpyplayer are excluded from the Android build

`requirements.txt` lists `opencv-python` and `ffpyplayer` as **optional**
on desktop, and the app is already written to gracefully fall back
without them (see `MEDIA_GUIDE.md` and `services/camera_service.py`).
Both packages need real native compilation to cross-build for Android,
which significantly increases build time and is a common source of
Buildozer build failures — exactly the kind of fragile dependency
problem you already hit once trying to install Kivy on Windows. Leaving
them out keeps this Android build fast and reliable for a first pass.

If you want a real Android camera or real video playback later, that's
a separate, follow-up piece of work — not something to bolt on while
still getting the first APK build working.

## If the build fails

Click into the failed run and open the "Build the debug APK" step to
see the actual error. The most common causes are:

- A typo in `buildozer.spec` (re-check indentation/section headers if
  you hand-edit it).
- A requirement that doesn't have an Android build recipe available.
  If you add a new Python package to the app later, check first
  whether python-for-android has a recipe for it before adding it to
  buildozer.spec's requirements line.

Paste the error back and it can be diagnosed from there.
