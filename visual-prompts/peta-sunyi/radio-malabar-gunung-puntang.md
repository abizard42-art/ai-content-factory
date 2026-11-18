# Visual Prompt Pack — Radio Malabar, Gunung Puntang

**Channel:** Peta Sunyi  
**Versi:** Claude Visual Director — production draft  
**Format:** 9:16 vertical, 2D cinematic hand-painted illustration  
**Penggunaan:** Setiap AI Image Prompt digabungkan dengan MASTER STYLE PROMPT. Setiap Negative Prompt scene digabungkan dengan BASE NEGATIVE PROMPT.

## Catatan integrasi pipeline

Renderer episode saat ini menggunakan aset AI untuk shot `01A`, `03A`, `04A`, `05A`, `06A`, dan `08A`. Shot `MAP`, `FACT`, dan `END` tetap dibuat otomatis sebagai grafis oleh renderer. Prompt scene 2, 7, dan 9 di bawah disimpan sebagai referensi visual/opsi alternatif, bukan aset wajib pada konfigurasi render saat ini.

**Nama file aset AI yang dipakai renderer:**
- Scene 1 → `peta-sunyi-01A.jpg`
- Scene 3 → `peta-sunyi-03A.jpg`
- Scene 4 → `peta-sunyi-04A.jpg`
- Scene 5 → `peta-sunyi-05A.jpg`
- Scene 6 → `peta-sunyi-06A.jpg`
- Scene 8 → `peta-sunyi-08A.jpg`

## 1. MASTER STYLE PROMPT

Tempel di akhir semua AI Image Prompt:

`2D cinematic hand-painted illustration, documentary mystery animation style, painterly matte-painting texture with subtle film grain, muted palette of dark forest green, fog grey and deep umber brown, low-key lighting with strong contrast and volumetric fog, rich environmental detail (tropical trees, moss, wet concrete, rusted metal, ferns), strong foreground/midground/background depth, atmospheric and quietly eerie but beautiful, vertical 9:16 composition, no text, no watermark, no logo`

### BASE NEGATIVE PROMPT

Tempel di semua scene:

`photorealistic, photograph, 3D render, CGI, anime, manga, chibi, children's book style, cute cartoon, text, letters, subtitles, watermark, logo, signature, gore, blood, severed body parts, skull, extra limbs, deformed anatomy, bright saturated colors, neon, modern buildings, vehicles, tourists, tents, generic AI fantasy look`

## 2. ENVIRONMENT CONSISTENCY LOCK

Gunakan deskripsi lingkungan ini berulang kali agar semua gambar terasa berada di tempat yang sama:

- Lembah hutan pegunungan tropis Gunung Puntang, Jawa Barat.
- Dua punggung bukit hijau gelap membingkai lembah.
- Reruntuhan bangunan pemancar berupa struktur beton rendah memanjang dengan bukaan jendela kosong.
- Jembatan beton tua melengkung kecil di atas aliran sungai berbatu.
- Lumut, akar, pakis, tanah basah, besi berkarat, dan kabut berlapis.
- Waktu dominan blue hour hingga malam berkabut; kilas balik sejarah memakai palet sepia-hijau.
- Jangan mengarang detail arsitektur spesifik yang tidak terlihat di referensi lokasi. Interior pemancar adalah rekonstruksi artistik.

## 3. SCENE PROMPTS

### Scene 1 — HOOK (0–6 detik) | Asset: 01A

**Fungsi:** Menangkap perhatian dalam 1–2 detik dengan kontras kuat dan kesan ada yang salah.

**Deskripsi:** Close-up bingkai jendela beton tua yang gelap. Di baliknya, kabut pucat dan siluet manusia jauh yang hampir larut dalam kabut.

**AI Image Prompt:**

`Extreme close-up from inside a pitch-dark ruined concrete wall, looking through a tall rectangular window opening framed by moss, rust stains and exposed orange rebar. Beyond it, a pale glowing wall of fog in a night forest. In the far distance, one lone human silhouette in worn early-20th-century work clothes, normal human proportions, facial features completely obscured by dense mist. The figure is ambiguous and never visibly dismembered or physically headless. Strong foreground darkness, cold teal-green rim light on the window edges, dripping water, ferns at the bottom of the frame.`

**Camera/Motion Prompt:**

`Very slow push-in through the window opening. Fog drifts left to right. The distant silhouette stays still, then gradually fades back into the mist over the last second. Faint flicker of cold light.`

**Negative Prompt khusus:**

`visible face, visible facial features, physically headless body, severed neck, blood, multiple figures, bright background, daylight, close-up person`

### Scene 2 — LOKASI (6–11 detik) | Referensi alternatif; renderer memakai MAP

**Fungsi:** Menegaskan satu lokasi dan satu mood: lembah, kabut, puing.

**Deskripsi:** Establishing shot lembah Gunung Puntang saat senja. Puing beton di tengah hutan, dua punggung bukit membingkai.

**AI Image Prompt:**

`Wide establishing shot of a misty forested valley on Mount Puntang, West Java, Indonesia, at blue hour. Two steep dark-green ridges frame the scene. In the midground, a long, low weathered concrete ruin with a row of empty window openings sits among tall trees. A narrow stream and a small old arched concrete bridge are barely visible at the lower right. Layers of fog between the trees, a dim silver-grey sky, moss-covered ground, tropical ferns in the foreground. Establish a distinctive valley layout that can be reused consistently in later shots.`

**Camera/Motion Prompt:**

`Slow aerial descent toward the ruin with parallax between the fog layers. Fog moves gently. Subtle zoom-in at the end.`

**Negative Prompt khusus:**

`tourists, tents, cars, modern buildings, roads, bright sunshine, people, village lights, urban skyline`

### Scene 3 — SEJARAH (11–17 detik) | Asset: 03A

**Fungsi:** Menunjukkan awal pembangunan 1917 sebagai kontras dengan puing masa kini.

**Deskripsi:** Ilustrasi bergaya arsip: tiang baja dan kabel panjang dibangun di lembah yang sama, warna lebih pudar dan sepia-hijau.

**AI Image Prompt:**

`Archival-style 2D illustration of the early construction of a long-distance radio station in a West Java mountain valley in 1917: tall steel lattice masts rising on the ridges, thick cables stretching across the valley between two mountain peaks, period-appropriate bamboo scaffolding, a half-built concrete hall in the midground, and a few tiny distant workers as indistinct silhouettes. Faded sepia-green duotone, aged archival illustration feel but still painted, soft paper grain, hazy sky, the same two-ridge valley layout as the present-day establishing shot. Historically plausible early-20th-century construction equipment only.`

**Camera/Motion Prompt:**

`Slow lateral pan following the cables from left to right. Light grain and gentle film flicker. The image desaturates slightly at the end.`

**Negative Prompt khusus:**

`clear faces of workers, modern machinery, modern cranes, colorful modern clothes, text, captions, border frame, photorealism`

### Scene 4 — KEJAYAAN (17–23 detik) | Asset: 04A

**Fungsi:** Menunjukkan puncak kejayaan teknologi sebelum lembah kembali sunyi.

**Deskripsi:** Rekonstruksi artistik ruang mesin pemancar tanpa orang, mesin besar dan meja telegraf. Garis cahaya tipis keluar dari jendela dan melintasi lembah ke langit.

**AI Image Prompt:**

`Artistic historical reconstruction of an early-1920s long-distance radio transmitter hall, empty of people: massive period-appropriate riveted metal machinery, glass vacuum tubes glowing warm amber, thick copper coils, a wooden desk with a brass Morse telegraph key and vintage headphones in the foreground. Through a tall industrial window, a thin symbolic line of pale golden light extends over the foggy mountain valley toward the distant sky, suggesting a signal crossing continents. Deep shadows, warm amber highlights against cool green-grey surroundings, richly detailed hand-painted environment. This is an evocative reconstruction, not a claim to depict the exact surviving interior.`

**Camera/Motion Prompt:**

`Slow dolly forward along the desk toward the window. The tubes pulse faintly. The thin symbolic line of light slowly extends out of the window and into the sky.`

**Negative Prompt khusus:**

`people, crowds, faces, modern screens, computers, LED lights, readable text, legible dials, modern radio equipment, world map`

### Scene 5 — LEGENDA (23–29 detik) | Asset: 05A

**Fungsi:** Memperkenalkan Bejo sebagai cerita warga, bukan fakta yang sudah terverifikasi.

**Deskripsi:** Sorot senter menyapu dinding lumut. Bayangan seseorang jatuh di dinding, orangnya tidak terlihat.

**AI Image Prompt:**

`Close shot of a moss-covered concrete wall at night inside the same Radio Malabar ruins. A narrow cold white flashlight beam sweeps across it, revealing cracks, rust streaks and wet texture. The long shadow of a lone person in old work clothes is cast on the wall, while the shadow's head and facial outline dissolve ambiguously into the beam's haze. The person remains out of frame. Dark green and umber tones, heavy shadow, drifting fog at the bottom of the frame. Quiet folkloric mystery, not a literal depiction of violence.`

**Camera/Motion Prompt:**

`Flashlight beam slowly sweeps across the wall from left to right. The shadow stretches and slides, then slips out of frame. Slight handheld sway.`

**Negative Prompt khusus:**

`visible person, visible face, visible hands, physically headless body, blood, gore, ghost with glowing eyes, bright lamp, text`

### Scene 6 — MISTERI (29–37 detik) | Asset: 06A

**Fungsi:** Membangun ketakutan lewat jembatan, kabut, angin, dan penampakan samar.

**Deskripsi:** Jembatan tua dari sisi samping. Di tengahnya berdiri siluet manusia jauh, nyaris tertutup kabut.

**AI Image Prompt:**

`Medium-wide side view of the same small old arched concrete bridge over a dark rocky stream in the Mount Puntang forest. Corroded iron railing and wet moss cover the surfaces. Thick fog hangs around the bridge. At its center stands one faint human silhouette, far from the camera, in worn work clothes, with normal human proportions and facial features completely obscured by dense fog. The figure is ambiguous and never visibly dismembered or physically headless. Overhanging tree branches in the dark foreground bend slightly in the wind. Cold grey-green light, deep black shadows, faint mist rising from the water. Preserve the same bridge and valley environment established in previous scenes.`

**Camera/Motion Prompt:**

`Camera stays almost static with a very slow drift to the right. Fog thickens and rolls across the bridge. For a split second the silhouette is visible, then the mist covers it. Branches sway.`

**Negative Prompt khusus:**

`visible face, eyes, blood, gore, severed head, floating head, zombie, ghost in white dress, bright moon, tourists, physically headless body`

### Scene 7 — FAKTA VS LEGENDA (37–45 detik) | Referensi alternatif; renderer memakai FACT

**Fungsi:** Memisahkan yang tercatat dari yang diceritakan.

**Deskripsi:** Komposisi dua panel vertikal. Atas: ilustrasi arsip pemancar yang jelas. Bawah: hutan gelap berkabut dengan siluet samar.

**AI Image Prompt:**

`A carefully composed vertical two-panel 2D illustration separated by a torn aged-paper edge. Top panel: a clear, sharply drawn sepia archival-style illustration of the radio station's steel masts, cables and concrete hall in the same mountain valley, with an orderly documented historical atmosphere. Bottom panel: a dark foggy forest path at night with one faint, barely visible human silhouette among the trees, soft blurred edges, uncertain and dreamlike. Strong contrast between crisp archival lines above and atmospheric haze below. No written labels or typography; the distinction is communicated only through visual style.`

**Camera/Motion Prompt:**

`Top panel stays steady. Bottom panel has drifting fog and a subtle flicker. Slow downward camera tilt across the paper edge, then a gentle push-in on the bottom panel.`

**Negative Prompt khusus:**

`text, labels, dates, numbers, captions, split-screen user interface, photo collage, clear face, illegible typography`

### Scene 8 — CLIMAX (45–52 detik) | Asset: 08A

**Fungsi:** Puncak ketegangan lewat suara dan gerak yang minim.

**Deskripsi:** POV berjalan di tanah basah reruntuhan. Jejak sepatu terisi air, siluet jauh di kabut.

**AI Image Prompt:**

`Low-angle ground-level point-of-view shot of a wet muddy path through the same Radio Malabar ruins at night. In the foreground, a single fresh boot print slowly filling with water, tiny ripples on its surface. The old concrete ruin walls loom in the midground, with faint cold light from one empty window. In the distant fog, a tiny human silhouette stands still beside the same arched bridge, facial features fully obscured by mist and normal human proportions maintained. Deep shadows, rain-like droplets, muted green-grey and brown palette, strong depth with foreground mud, midground ruin and background fog.`

**Camera/Motion Prompt:**

`Slow forward walking motion at ankle height. Ferns sway in the wind, then everything freezes. A single ripple spreads across the boot print. Fog rolls forward and the distant silhouette disappears by the final frame.`

**Negative Prompt khusus:**

`running figure, monster, jump-scare face, blood, gore, bright flash, multiple silhouettes, tourists, physically headless body`

### Scene 9 — ENDING (52–58 detik) | Referensi alternatif; renderer memakai END

**Fungsi:** Meninggalkan pertanyaan: siapa yang masih menunggu?

**Deskripsi:** Pandangan dari dalam bingkai jendela reruntuhan ke arah jembatan. Kabut menutup, siluet sangat kecil di jembatan.

**AI Image Prompt:**

`Composition looking out from inside a ruined concrete window frame toward the same old arched bridge at blue-hour dusk. Dark moss-covered concrete and rusted rebar frame the left and right edges. Beyond, fog closes over the valley and the stream. On the bridge, barely visible, one tiny still human silhouette stands in the distance, with normal human proportions and facial features completely obscured by mist. Dim blue-green twilight, fading silver light in the sky, huge empty space around the figure. Quiet, unresolved, haunting atmosphere.`

**Camera/Motion Prompt:**

`Very slow pull-back from the window frame. Fog gradually swallows the bridge and the distant silhouette. Final frame fades to near-black with only the window outline faintly visible.`

**Negative Prompt khusus:**

`clear human face, text, bright sunset, saturated dramatic sky colors, crowd, physically headless body, gore, user interface elements`

## 4. PRIORITAS GENERASI

1. **Scene 1 / 01A:** visual hook; harus terbaca kuat dalam satu detik.
2. **Scene 6 / 06A:** visual misteri utama; jembatan dan siluet harus konsisten.
3. **Scene 4 / 04A:** rekonstruksi sejarah; hindari tampilan teknologi modern.
4. **Scene 3 / 03A:** kilas balik arsip; jaga palet sepia-hijau.
5. **Scene 5 / 05A dan Scene 8 / 08A:** detail atmosfer dan kesinambungan lingkungan.

## 5. CATATAN SEBELUM GENERATE

- Buat satu gambar environment reference terlebih dahulu dari Scene 2. Gunakan sebagai referensi visual untuk scene reruntuhan, jembatan, dan lembah berikutnya bila image generator mendukung image reference.
- Jangan menggambarkan Bejo sebagai tubuh yang secara literal kehilangan kepala. Sosok harus jauh, normal secara anatomi, dan tertutup kabut.
- Prompt sejarah dan interior adalah ilustrasi rekonstruksi; jangan menambahkan teks arsip atau detail faktual yang tidak didukung sumber.
- Render gambar diam dahulu. Camera/Motion Prompt dipakai pada tahap image-to-video, bukan ditempel ke prompt gambar diam.
