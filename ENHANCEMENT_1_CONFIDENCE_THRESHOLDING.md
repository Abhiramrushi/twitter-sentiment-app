# Enhancement 1: Confidence Thresholding

## Summary

This enhancement adds confidence threshold support to the sentiment prediction API and frontend UI.

## What's new

- `threshold` parameter in request payload.
- Backend converts threshold values from either 0-1 or 0-100 ranges.
- Response includes `meets_threshold`, `threshold_used`, and a warning message when confidence is low.
- Frontend allows users to set a threshold slider and shows status icons.

## API Example

Request:
```json
{
  "text": "I love this new feature!",
  "threshold": 0.75
}
```

Response:
```json
{
  "text": "I love this new feature!",
  "sentiment": "Positive",
  "confidence": 0.92,
  "confidence_percentage": 92.0,
  "label_scores": {"Negative": 0.03, "Neutral": 0.05, "Positive": 0.92},
  "meets_threshold": true,
  "threshold_used": 0.75,
  "warning": null
}
```
