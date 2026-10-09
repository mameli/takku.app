"""Writes the hand-drawn diagram into public/index.html, replacing the <figure class="schematic">.

    python3 tools/drawing.py public/index.html
"""
import random
import re
import sys

random.seed(11)


def scribble(x0, x1, y, tall=0.1):
    """A line of fake handwriting: words of small humps, with an ascender now and then."""
    parts = []
    x = x0
    while x < x1 - 12:
        width = random.uniform(12, 38)
        end = min(x + width, x1)
        parts.append(f"M{x:.1f} {y:.1f}")
        cx = x
        while cx < end:
            step = random.uniform(3.2, 4.6)
            if random.random() < tall:
                h = random.uniform(5.5, 7.5)
                parts.append(f"c{-step * 0.3:.1f} {-h:.1f} {step * 0.9:.1f} {-h:.1f} {step:.1f} 0")
            else:
                h = random.uniform(2.4, 4)
                parts.append(f"c{step * 0.1:.1f} {-h:.1f} {step * 0.9:.1f} {-h:.1f} {step:.1f} 0")
            cx += step
        x = end + random.uniform(4.5, 8)
    return "".join(parts)


def lines(x0, x1, ys, last_short=True):
    out = []
    for i, y in enumerate(ys):
        end = x1 - (random.uniform(30, 70) if last_short and i == len(ys) - 1 else random.uniform(0, 14))
        out.append(scribble(x0, end, y))
    return out


# Transcript: you (red), then the two people on the call (blue, green).
t = lines(142, 318, [284, 300, 316, 332, 348, 364, 380], last_short=False)
transcript = (
    f'<path class="ink-red" d="{t[0]}{t[1]}"/>'
    f'<path class="ink-blue" d="{t[2]}{t[3]}"/>'
    f'<path class="ink-green" d="{t[4]}"/>'
    f'<path class="ink-red" d="{t[5]}{t[6]}"/>'
)

# Meeting note: the summary highlighted on top, a marked moment, then your notes.
n = lines(108, 256, [520, 536, 552, 576, 592], last_short=False)
note = (
    '<path class="highlight" d="M104 520h150M104 536h150M104 552h96"/>'
    f'<path class="ink-graphite" d="{n[0]}{n[1]}{n[2][:len(n[2]) // 2]}"/>'
    f'<path class="ink-graphite light" d="{n[3]}{n[4]}"/>'
)

svg = f'''<figure class="schematic">
      <svg viewBox="0 0 520 660" role="img" aria-labelledby="drawing-title drawing-desc">
        <title id="drawing-title">How Takku works</title>
        <desc id="drawing-desc">Your microphone and the call go into a transcript, written on your Mac, with each speaker in a different colour. The transcript becomes a meeting note in your Obsidian vault, with the summary on top. The summary is written by a model on your Mac or by a provider you choose. The audio stays on your Mac.</desc>
        <defs>
          <!-- Coloured pencil: grain inside the stroke, edges not quite straight -->
          <filter id="crayon" x="-10%" y="-10%" width="120%" height="120%">
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" result="grain"/>
            <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  3.2 0 0 0 -0.95" result="mask"/>
            <feComposite in="SourceGraphic" in2="mask" operator="in" result="grainy"/>
            <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="9" result="warp"/>
            <feDisplacementMap in="grainy" in2="warp" scale="3.5" xChannelSelector="R" yChannelSelector="G"/>
          </filter>
          <filter id="wobble" x="-5%" y="-5%" width="110%" height="110%">
            <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="7" result="noise"/>
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.4" xChannelSelector="R" yChannelSelector="G"/>
          </filter>
        </defs>

        <!-- Your Mac -->
        <rect x="20" y="42" width="490" height="598" rx="28" class="boundary" filter="url(#wobble)"/>
        <text x="26" y="30" class="hand graphite-text">your Mac</text>

        <!-- Microphone, in red: you -->
        <g filter="url(#crayon)">
          <rect x="94" y="80" width="34" height="58" rx="17" class="fill-red"/>
        </g>
        <g filter="url(#wobble)" class="outline">
          <rect x="94" y="80" width="34" height="58" rx="17"/>
          <path d="M101 96h20M101 106h20M101 116h20"/>
          <path d="M84 118c0 26 12 36 27 36s27-10 27-36M111 154v18M92 174h38"/>
        </g>

        <!-- The call: a window with the two people, in blue and green -->
        <g filter="url(#crayon)">
          <path d="M240 80h130v14H240z" class="fill-graphite"/>
          <circle cx="278" cy="118" r="11" class="fill-blue"/>
          <path d="M258 158c2-16 10-24 20-24s18 8 20 24z" class="fill-blue"/>
          <circle cx="334" cy="118" r="11" class="fill-green"/>
          <path d="M314 158c2-16 10-24 20-24s18 8 20 24z" class="fill-green"/>
        </g>
        <g filter="url(#wobble)" class="outline">
          <rect x="240" y="80" width="130" height="86" rx="8"/>
          <path d="M240 94h130"/>
        </g>

        <!-- Into the transcript -->
        <g filter="url(#wobble)" class="arrow">
          <path pathLength="1" class="trace" d="M114 186c4 34 40 50 70 70"/>
          <path pathLength="1" class="trace" d="M322 198c0 26-16 42-36 58"/>
          <path class="trace head" d="M184 256l-13-1M184 256l-5-12"/>
          <path class="trace head" d="M286 256l3-13M286 256l12-4"/>
        </g>

        <!-- Transcript, taped down -->
        <g transform="rotate(-2 230 328)">
          <rect x="125" y="254" width="210" height="146" class="sheet-paper" filter="url(#wobble)"/>
          <g filter="url(#wobble)" class="scribbles">{transcript}</g>
        </g>
        <rect x="198" y="243" width="62" height="18" class="tape" transform="rotate(5 229 252)"/>

        <!-- To the summary and back, and down to the note -->
        <g filter="url(#wobble)" class="arrow">
          <path pathLength="1" class="trace late" d="M344 324c14-6 30-8 42-6"/>
          <path pathLength="1" class="trace later" d="M410 366c-2 66-40 126-140 146"/>
          <path pathLength="1" class="trace late" d="M220 408c-2 24-24 40-40 56"/>
          <path class="trace head late" d="M386 318l-11-6M386 318l-10 7"/>
          <path class="trace head later" d="M270 512l11 5M270 512l8-9"/>
          <path class="trace head late" d="M180 464l12-2M180 464l2-12"/>
        </g>

        <!-- The summary, labelled above as the mic and the call -->
        <g filter="url(#crayon)">
          <rect x="388" y="294" width="72" height="64" rx="10" class="fill-blue"/>
          <path d="M424 308v36M406 326h36M411 313l26 26M437 313l-26 26" class="sparkle"/>
        </g>

        <!-- Meeting note, a notepad as in the icon -->
        <rect x="92" y="482" width="176" height="130" rx="6" class="sheet-paper" filter="url(#wobble)"/>
        <g filter="url(#wobble)" class="scribbles">{note}
          <path d="M98 588l4-8 4 8-8-5h8z" class="sparkle-red"/>
        </g>
        <g filter="url(#wobble)" class="outline">
          <path d="M136 494c-8 0-10-22 0-22s8 22 0 22M224 494c-8 0-10-22 0-22s8 22 0 22"/>
        </g>

        <text x="66" y="66" class="hand">your mic</text>
        <text x="248" y="66" class="hand">the call</text>
        <text x="240" y="186" class="hand small graphite-text">Meet, Zoom, Teams…</text>
        <text x="30" y="430" class="hand">the transcript</text>
        <text x="30" y="448" class="hand small graphite-text">Whisper or Parakeet</text>
        <text x="30" y="294" class="hand red-text">the audio</text>
        <text x="30" y="314" class="hand red-text">stays</text>
        <text x="30" y="334" class="hand red-text">in here</text>
        <text x="386" y="226" class="hand">the summary</text>
        <text x="386" y="245" class="hand small graphite-text">on your Mac, or</text>
        <text x="386" y="263" class="hand small graphite-text">a provider you</text>
        <text x="386" y="281" class="hand small graphite-text">choose</text>
        <text x="280" y="566" class="hand">meeting note</text>
        <text x="280" y="585" class="hand small graphite-text">in your Obsidian</text>
        <text x="280" y="603" class="hand small graphite-text">vault</text>
      </svg>
    </figure>'''

path = sys.argv[1]
html = open(path).read()
html, count = re.subn(r'<figure class="schematic">.*?</figure>', lambda _: svg, html, flags=re.S)
assert count == 1
open(path, "w").write(html)
