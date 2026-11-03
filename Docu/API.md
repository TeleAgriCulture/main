# Get your data with the API

Readings from every published kit are open data. You can fetch them from
`https://kits.teleagriculture.org` with anything that makes a web request,
such as a browser, `curl`, Python or a web page of your own.

Reading data needs no account and no key. Sending readings from your own
device needs the kit's API key.

Every response is JSON. Results are in a top-level `data` key, and paging
details sit next to it in `links` and `meta`. All times are UTC, in ISO 8601.

## Contents

- [Quick start](#quick-start)
- [List the published kits](#list-the-published-kits)
- [One kit and its latest readings](#one-kit-and-its-latest-readings)
- [A sensor's history](#a-sensors-history)
- [Daily average, minimum and maximum](#daily-average-minimum-and-maximum)
- [Send readings from your own device](#send-readings-from-your-own-device)
- [Other public endpoints](#other-public-endpoints)
- [Errors, limits and caching](#errors-limits-and-caching)
- [Open data and questions](#open-data-and-questions)

## Quick start

1. Find a kit id in the [list of published kits](#list-the-published-kits).
2. Fetch [that kit](#one-kit-and-its-latest-readings) to see its sensors.
3. Download a sensor's [history](#a-sensors-history) or its
   [daily averages](#daily-average-minimum-and-maximum).

```bash
curl https://kits.teleagriculture.org/api/public/kits
curl https://kits.teleagriculture.org/api/kits/1001
curl https://kits.teleagriculture.org/api/kits/1001/temp/measurements
```

## List the published kits

> `GET https://kits.teleagriculture.org/api/public/kits`

Returns every kit its owner has published, 30 per page, oldest first. Each kit
lists the names and units of its sensors. Readings are not included.

`coordinates` is only as precise as the owner chose to publish. `precision`
names the level and `precision_m` gives it roughly in metres. For a kit that
publishes only its country, `coordinates` is `null`.

`is_active` is `true` when the kit has sent a reading within its reporting
interval. That interval is 24 hours unless the owner set another.

```json
{
  "data": [
    {
      "id": 1001,
      "name": "Salzburg Rooftop",
      "location": "Salzburg",
      "country_code": "AT",
      "coordinates": {
        "lat": 47.8,
        "lng": 13.05,
        "precision": "approximate",
        "precision_m": 1113,
        "source": "owner"
      },
      "is_active": true,
      "last_measurement_at": "2026-09-09T14:45:25.000000Z",
      "sensors": [
        { "name": "temp", "unit": "celcius" },
        { "name": "hum", "unit": "%" }
      ]
    }
  ],
  "links": {
    "first": null,
    "last": null,
    "prev": null,
    "next": "https://kits.teleagriculture.org/api/public/kits?page%5Bcursor%5D=eyJpZCI6MTAzMH0"
  },
  "meta": {
    "path": "https://kits.teleagriculture.org/api/public/kits",
    "per_page": 30,
    "next_cursor": "eyJpZCI6MTAzMH0",
    "prev_cursor": null
  }
}
```

To get the next page, follow `links.next`, or add `page[cursor]=` with the
value of `meta.next_cursor`. When `next_cursor` is `null`, you have every kit.

## One kit and its latest readings

> `GET https://kits.teleagriculture.org/api/kits/[KIT_ID]`

Returns the kit and every sensor configured on it, each with its most recent
reading. A sensor that has never reported has no `latest_measurement`, or has
it set to `null`.

The kit's own `latest_measurement` is the newest reading from any of its
sensors. Each sensor keeps a separate history, so there is no single set of
"latest readings" for a kit.

A kit that is not published returns `404 Not Found` to anyone who is not a
member of it.

```json
{
  "data": {
    "id": 1001,
    "name": "Salzburg Rooftop",
    "location": "Salzburg",
    "country_code": "AT",
    "location_visibility": "approximate",
    "last_measurement_at": "2026-09-09T14:45:25.000000Z",
    "is_active": true,
    "reporting_interval_hours": null,
    "latitude": 47.8,
    "longitude": 13.05,
    "coordinates_precision": "approximate",
    "coordinates_precision_m": 1113,
    "coordinates_source": "owner",
    "latest_measurement": {
      "created_at": "2026-09-09T14:45:25.000000Z",
      "value": 34.14
    },
    "alerts": [],
    "sensors": [
      {
        "id": 1,
        "name": "hum",
        "group": "Air",
        "unit": "%",
        "latest_measurement": {
          "created_at": "2026-09-09T14:45:25.000000Z",
          "value": 34.14
        }
      }
    ],
    "projects": []
  }
}
```

## A sensor's history

> `GET https://kits.teleagriculture.org/api/kits/[KIT_ID]/[SENSOR_NAME]/measurements`
>
> `[SENSOR_NAME]` is the sensor's name as the kit shows it, for example `temp`
> or `CO`. Upper and lower case are treated the same.

Returns the newest readings first, 30 per page. `page[size]` can ask for fewer.
Asking for more than 30 still returns 30.

```json
{
  "data": [
    { "created_at": "2026-09-09T14:45:25.000000Z", "value": -2.05 },
    { "created_at": "2026-09-09T13:45:25.000000Z", "value": -3.05 }
  ],
  "links": {
    "first": null,
    "last": null,
    "prev": null,
    "next": "https://kits.teleagriculture.org/api/kits/1001/temp/measurements?page%5Bcursor%5D=eyJj..."
  },
  "meta": {
    "path": "https://kits.teleagriculture.org/api/kits/1001/temp/measurements",
    "per_page": 30,
    "next_cursor": "eyJj...",
    "prev_cursor": null
  }
}
```

To go further back in time, follow `links.next`, or add `page[cursor]=` with
the value of `meta.next_cursor`.

A sensor name the kit does not have returns `404 Not Found`.

## Daily average, minimum and maximum

> `GET https://kits.teleagriculture.org/api/kits/[KIT_ID]/[SENSOR_NAME]/measurements/[PERIOD]`
>
> `[PERIOD]` is `week` for 7 days, `month` for 28 days or `year` for 365 days.

Returns one row per day, ending on the day of the sensor's newest reading. A
day without readings has `null` for `avg`, `min` and `max`. `weekday` runs from
0 for Sunday to 6 for Saturday.

```json
{
  "data": [
    { "date": "2026-09-08", "weekday": 2, "avg": -3.35208333, "min": -5, "max": 0.9 },
    { "date": "2026-09-09", "weekday": 3, "avg": -0.68666667, "min": -4.8, "max": 4.2 }
  ],
  "meta": {
    "from": "2026-09-03",
    "to": "2026-09-09",
    "next_cursor": "2026-09-16",
    "prev_cursor": "2026-09-02"
  }
}
```

To see an earlier period, add `page[cursor]=` with the date in
`meta.prev_cursor`. Cursors are dates in the form `YYYY-MM-DD`, and the period
ends on that date.

If the sensor has no readings on or before the cursor date, the response is
`404 Not Found`. A cursor that is not a date returns
`422 Unprocessable Content`.

## Send readings from your own device

> `POST https://kits.teleagriculture.org/api/kits/[KIT_ID]/measurements`

The TeleAgriCulture board sends every WiFi reading through this endpoint, and
any other device or script can do the same. LoRaWAN boards report through
The Things Network instead and do not use it.

**Authentication.** Send the kit's API key as `Authorization: Bearer [API_KEY]`.
Kit members find the key on the kit's **Edit** page, under **API Security**.

**Body.** A JSON object that maps sensor names to numbers. A failed reading can
be sent as `NaN` or `null`, and the app skips it.

**Sensor names.** Each name must match a sensor set up on the kit, ignoring
case. The app does not record a name that matches no sensor. It lists that name
on the kit's Edit page under **Readings not set up**, where a member can add it
as a sensor or ignore it.

```bash
curl -X POST "https://kits.teleagriculture.org/api/kits/1001/measurements" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"temp": 21.5, "hum": 48}'
```

| Status | Meaning |
| --- | --- |
| `204 No Content` | The readings were received. |
| `400 Bad Request` | The body was not a JSON object. |
| `403 Forbidden` | The key is missing, wrong, revoked or belongs to another kit. |
| `429 Too Many Requests` | This kit sent more than 60 requests in the last minute. |

## Other public endpoints

The app's map and project pages use these, and anyone can call them.

| Endpoint | Returns |
| --- | --- |
| `GET /api/public/globe` | Kit counts per country. |
| `GET /api/public/countries/[CODE]` | The published kits in one country, by two-letter code such as `AT`. |
| `GET /api/public/projects` | Published projects. |
| `GET /api/public/projects/[SLUG]` | One published project and its kits. |

## Errors, limits and caching

Errors are JSON with a `message` that describes the problem.

Reading endpoints under `/api/kits` allow 240 requests a minute per IP address.
Above that they return `429 Too Many Requests`. Wait a minute, then continue.

Responses from `/api/public` are cached. They can be up to five minutes old,
so poll them no more often than that.

The API accepts requests from any website, so a web page on your own domain
can call it directly from the browser.

## Open data and questions

Readings from published kits may be viewed, downloaded and reused. The
[terms of use](https://kits.teleagriculture.org/terms) have the details.

If something here does not match what the API returns, or you have a question,
write to letmegrow@teleagriculture.org.
