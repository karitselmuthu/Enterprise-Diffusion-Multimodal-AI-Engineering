# Human review workflow

The incident analyzer returns a proposed severity and source-linked observations. Local VLM output is explicitly marked `unverified_model_output`; it never raises severity by itself. A reviewer can inspect the stored analysis and record a single decision.

1. Set `REVIEW_API_KEY` to a long random value and start the API. Set `REVIEW_DB_PATH` to a persistent SQLite file location if the default `data/reviews.sqlite3` is unsuitable.
2. Submit `POST /reviews` with the same fields as `/multimodal/analyze` and an `X-Review-Key` header. The response has `status: "pending"` and an ID.
3. Use `GET /reviews` or `python scripts/review_lab.py` to inspect the report text, document extraction, image statistics, and any unverified VLM output.
4. Send `POST /reviews/{id}/decision` with `status: "approved"` or `"rejected"`, a reviewer identifier, a summary, and any cited evidence sources. Approval also requires a recommendation. A second decision receives HTTP 409.

Example decision body:

```json
{
  "status": "approved",
  "reviewer": "analyst-42",
  "summary": "The submitted report describes smoke in server room four; visual model text has not been independently verified.",
  "recommendation": "Verify the location against the dashboard and follow the site incident procedure.",
  "cited_sources": ["report_text"]
}
```

The shared API key controls access to this lab queue. Reviewer identifiers are supplied by the client and are not independently authenticated. Use a managed identity system, access logs, retention rules, and a production database before handling live enterprise incident data.
