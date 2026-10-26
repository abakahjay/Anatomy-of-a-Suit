# Film brief: The Anatomy of a Suit

One continuous shot, no cuts. The site scrubs through it as 535 frames, so every chapter must morph out of the one before.
Make it in an image-to-video model that supports start and end frames (Higgsfield, Kling 2.x, Veo, Runway, Seedance).
Generate each clip from the previous clip's last frame so the joins are seamless, then join them and run `tools/import-film.sh film.mp4`.

**Look for every clip:** dark charcoal-green studio, one soft overhead spotlight, faint haze, garment floating in mid-air over a reflective black floor, slow camera, photoreal fabric, 16:9, 24 fps, no text, no logos.

| # | Chapter (site copy) | Clip | Seconds |
|---|---|---|---|
| 0 | The Anatomy of a Suit | Empty spotlit stage, haze drifting, a faint ghost silhouette of a man standing under the light. Slow push in. | 3 |
| 1 | A Shirt of Pure Cotton | The silhouette dissolves into a crisp white cotton dress shirt floating alone, sleeves relaxed, slowly rotating a quarter turn. | 3 |
| 2 | Cut Close to the Body | A black waistcoat flies in from behind the camera in pieces and closes around the floating shirt, buttons fastening one by one. | 3 |
| 3 | Built on Full Canvas | The jacket assembles in mid-air: front panels, sleeves, collar and lapels drift in from all sides, exploded view, and lock together over the waistcoat. | 4 |
| 4 | The full cut | The finished three-piece suit hangs in the light, slow orbit, fabric settling. | 3 |
| 5 | Made to Be Worn | A man materialises inside the suit (head and hands fill in), stands, then fastens his cuffs. Face in shadow. | 3 |
| 6 | A Language of Colour | He steps forward and walks toward camera on a rain-wet night street with gas lamps; three more men join him, one in grey, one in cream, one in burgundy suits, walking in step. | 4 |
| 7 | The Last Quarter-Inch | Camera pushes into his sleeve: four working cuff buttons, a quarter-inch of white shirt cuff, then fade to black. | 3 |

Total about 26 s. The import script samples exactly 535 frames across the whole film, whatever its length.

**Phones:** either generate a 9:16 version with the same prompts, or keep the subject centred so the 16:9 film crops well (the script makes a centre-cropped portrait set automatically).
