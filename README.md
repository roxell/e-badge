# e-badge

A reusable conference badge for the Pimoroni Badger 2040 running Badger OS.
Three screens switchable with front buttons: A=badge, B=joke, C=QR vCard.

## Switching conferences

Conference files contain a single line with the conference name.
Personal info lives in `personal.txt` and is shared across conferences.
To switch conference, copy the right file to `badges/badge.txt` on the device:

```bash
make upload-config CONF=myconference2026.txt
```

Create a new conference file:

```bash
echo "MyConference 2026" > myconference2026.txt
make upload-config CONF=myconference2026.txt
```

## Config files

### Personal info (`personal.txt`)

One value per line, shared across all conferences:

| Line | Field                              |
|------|------------------------------------|
| 1    | Your name                          |
| 2    | Detail 1 label (e.g. "Email:")     |
| 3    | Detail 1 value                     |
| 4    | Detail 2 label (e.g. "IRC:")       |
| 5    | Detail 2 value                     |
| 6    | Detail 3 label (e.g. "GitHub:")    |
| 7    | Detail 3 value                     |
| 8    | Detail 4 label (e.g. "GitLab:")    |
| 9    | Detail 4 value                     |
| 10   | Image path on device               |
| 11   | Phone number                       |

See `example.personal.txt` for a template.

### Conference file

Single line with the conference name:

```
MyConference 2026
```

Details 1-2 (email, IRC) are shown on the badge screen.
All details are shown on the QR screen and included in the vCard.

## Jokes

Jokes are stored in `jokes.txt`, separated by `---` on its own line.
Each block is one joke with literal newlines for line breaks on screen.

```
Why do programmers
prefer dark mode?

Because light
attracts bugs.
---
There are 10 types
...
```

Upload jokes to the device:

```bash
uvx mpremote fs cp jokes.txt :/jokes.txt
```

If `/jokes.txt` is missing on the device, a built-in fallback list is used.

## Uploading to the Badger 2040

Plug in the Badger via USB. Uses `uvx` to run `mpremote` without
installing it globally.

```bash
# Check the device is visible
uvx mpremote connect list

# Upload badge app, image, jokes, and personal info
make upload-all

# Upload conference config
make upload-config CONF=myconference2026.txt

# Reset the device after uploading
make reset

# Or combine upload and reset
make upload-all reset
```

After uploading, the badge app appears in the Badger OS launcher.

## Images

- Pre-size to 80x80 pixels or smaller before uploading.
- Use baseline JPEG (not progressive -- the decoder cannot handle it).
- Monochrome or greyscale images work best on the 1-bit display.
- Store images in `/badges/` on the device.

## Common issues

- Progressive JPEGs will fail silently or raise an exception.
- Large images eat RAM fast; keep them small.
- The `mpremote fs cp` command has a bug where it skips files with the
  same size. The Makefile works around this by deleting before copying.
- The device halts after drawing (power saving). Unplug and replug USB
  between commands if the device stops responding.
