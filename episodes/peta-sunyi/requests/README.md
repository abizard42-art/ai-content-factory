# Peta Sunyi script generation requests

To start script generation automatically, add **one new JSON file per commit** in this folder.

Example filename: `villa-isola.json`

```json
{
  "topic": "Villa Isola, Bandung: sejarah pembangunan, Henri Maclaine Pont, pemilik awal, dan perubahan fungsi bangunan"
}
```

Rules:
- The JSON must contain a non-empty `topic` string.
- Add or update only one request JSON file in each commit.
- A push that changes a request JSON file starts the `Generate Peta Sunyi script` workflow.
- The workflow still saves the package for human review; it does not render or publish a video.
- Keep request filenames unique so a previous request is not accidentally overwritten.
