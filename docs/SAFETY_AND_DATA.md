# Safety, Privacy, and Data Quality

## Air-quality guidance

- Show the applicable AQI scale and source; do not mix national AQI scales without explicit conversion and explanation.
- Display freshness and location coverage. A nearby station is not a personal exposure monitor.
- Use official public-health guidance for high-pollution advisories and vulnerable groups.
- Encourage users with symptoms or health concerns to contact a qualified professional.
- Do not diagnose, prescribe, or promise that a mask, purifier, plant, or household hack eliminates exposure.
- Do not suggest opening windows is always beneficial; indoor and outdoor conditions matter.

## Generative AI boundaries

Gemini should explain verified inputs rather than act as an AQI sensor. The model must:
- receive normalized source data and timestamps;
- clearly label uncertainty and missing data;
- avoid invented readings, citations, health claims, or emissions totals;
- provide practical, non-alarmist suggestions;
- point to official local advisories when conditions are severe.

## Privacy

- Ask for the least precise location that can support the feature.
- Make location entry optional and explain why it is used.
- Do not collect names, medical records, or household identifiers for the MVP.
- Do not log secrets, raw precise coordinates, or sensitive free-text inputs.
