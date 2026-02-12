Place your desired background image in this folder and name it `ev_bg.jpg`.

Recommended steps:
1. Save the attached EV background image as `ev_bg.jpg`.
2. Put it here: static/images/ev_bg.jpg
3. Start the Django dev server and open the site; the image will be used as the page background.

Notes:
- The template uses the static path `images/ev_bg.jpg` and falls back to a gradient if the image is not present.
- For production, prefer a compressed image (e.g., WebP or optimized JPEG) and pin the asset or serve via a CDN.
